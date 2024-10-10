import os
import json
import requests
import telebot 
from telebot import types 
from dotenv import load_dotenv
import datetime as dt
import apscheduler
import importlib
from apscheduler.schedulers.background import BackgroundScheduler

from CONTANS import WEEKDAYNUMBER, BASE_URL, MAIN_COMMAND

def dynamic_import(module):
    return importlib.import_module(module)
#загрузка констант
load_dotenv()   
PASSWORD = os.getenv('PASSWORD')
TG_TOKEN = os.getenv('TG_TOKEN')
#запуск планировщика в фоне
background_scheduler  = BackgroundScheduler()
background_scheduler.start()

#экземпляр бота
bot = telebot.TeleBot(TG_TOKEN) 

#Клавиатура для создания напоминаний
inline1 = types.InlineKeyboardMarkup()
ik = types.InlineKeyboardButton(text = 'Ежедневно', callback_data = 'everyday')
ik2 = types.InlineKeyboardButton(text = 'По определенным дням недели', callback_data = 'inweek')
inline1.add(ik,ik2)

#начальная клава
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
item4 = types.KeyboardButton("Создание напоминания")
item3 = types.KeyboardButton("Просмотр напоминания приема")
item2 = types.KeyboardButton("Удаление напоминаний")
item1 = types.KeyboardButton('В начало!')
keyboard.add(item1, item2, item3, item4)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, reply_markup = keyboard, protect_content = True, text ="Привет! Там кнопочки снизу. Они могут добавить, удалить и посмотреть все твои напоминания.")
    
@bot.message_handler(commands=['copy'])
def copy_base_reminder(message):
    if str(message.chat.id) == PASSWORD:
        response = (requests.get(f'{BASE_URL}')).json()
        for i in response:
            username=i.get('chat')
            day_number = i.get('day')
            hour = i.get('hour')
            minute = i.get('minute')
            drug_name= i.get('med')
            intruction = i.get('add')
            id_last_user_remind = i.get('id') #берем ток id
            if day_number == 10:
                background_scheduler.add_job(send_remind, 'cron',hour=hour, minute=minute, id=str(id_last_user_remind), args=(username,drug_name,intruction))
            else:
                background_scheduler.add_job(send_remind, 'cron', day_of_week=day_number, hour=hour, minute=minute, id=str(id_last_user_remind), args=(username,drug_name,intruction))
            print(f'в расписание занесено{username}, принимает {drug_name} по {day_number} в {hour}:{minute}, доп инфа {intruction}')
        bot.send_message(message.chat.id, text=f'Успешно добавлено {len(response)} записей в расписания')
    else:
        bot.send_message(message.chat.id, text='У вас нет дотуступа к команде')

@bot.message_handler(content_types=["text"])
def distribution(message):
    if message.text == 'Создание напоминания':
        bot.send_message(message.chat.id, text='Выберите периодичность приема лекарства:', reply_markup=inline1)
    elif message.text == 'Просмотр напоминания приема':
        mes = api_list_remind(message)
        x = ''.join(mes.keys())
        bot.send_message(message.chat.id, text=f'{x}')
    elif message.text == 'Удаление напоминаний':
        bot.send_message(message.chat.id,text='Чтобы удалить напоминание напишите его айди.')
        x=''
        query = api_list_remind(message)
        for key,value in query.items():
            x = x + f'{key}\nАйди напоминания: {value}\n-------------------------------------\n'
        bot.send_message(message.chat.id,text=x)
        bot.register_next_step_handler(message, api_delete, id = query.values())
    elif message.text == 'В начало!':
        welcome(message)
    else:
        bot.send_message(message.chat.id,text='Я старался, но ничего не понял. Напишите заново.')


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'everyday':
        message=bot.send_message(call.message.chat.id, text='Напишите сообщение в формате: \n"Название медикомента; время приемов; дополнительная информация"\nПример: "Анальгин; 10:00, 11:00; По две таблетки, запивая водой"')
        bot.register_next_step_handler(message, create_remind, call.data)
    elif call.data == 'inweek':
       message=bot.send_message(call.message.chat.id, text='Напишите сообщение в формате: \n"Название медикомента; Дни недели приема; время приемов; дополнительная информация"\nПример: "Анальгин; Понедельник, Пятница; 10:00, 11:00; По две таблетки, запивая водой"')
       bot.register_next_step_handler(message, create_remind, call.data)

def create_remind(message,k):
    T = check_main_command(message)
    if T is False:
        parts = message.text.split(';')
        if k == 'everyday' and len(parts) == 3:
            drug_name = parts[0]  # Анальгин
            times = parts[1].split(',')  # ['10:00', '11:00']
            instruction = parts[2]  # По две таблетки, запивая водой
            # api_create_remind(message.chat.id,k,drug_name,times,instruction, weekday = 0)
            for i in times:
                time_parts = i.split(':')   #делаем время на часы и минуты
                if len(time_parts) == 2:
                    hour = int(time_parts[0])
                    print(hour)
                    if hour > 24 or hour < 0:
                        bot.send_message(message.chat.id,text=f'Не смог создать напоминание, ошибка точно есть в часе приема - {i}. Попробуйте написать сообщение заново')
                        bot.register_next_step_handler(message,create_remind, k)
                    else:
                        minute = int(time_parts[1])
                        if minute > 59 or minute < 0:
                                bot.send_message(message.chat.id,text=f'Не смог создать напоминание, ошибка точно есть в минутах приема - {i}. Попробуйте написать сообщение заново')
                                bot.register_next_step_handler(message, create_remind, k)
                        else:
                            requests.post(f'{BASE_URL}', json={"chat":f"{message.chat.id}",'hour':f'{hour}','minute':f'{minute}','med':f'{drug_name}','add':f'{instruction}'}) #добавляем в БД напоминалку
                            print(f'{message.chat.id} отправил в Бд напоминалку')
                            response = (requests.get(f'{BASE_URL}?chat={message.chat.id}')).json() #берем ее обратно, но уже с id
                            id_last_user_remind = (response[-1]).get('id') #берем ток id
                            start_remind(message.chat.id,drug_name,hour,minute,instruction,id_last_user_remind,k, day_number=0)
                            minute= f'0{minute}' if minute < 10 else minute
                            hour = f'0{hour}' if hour < 10 else hour
                            bot.send_message(message.chat.id, text=f'Запомнил!Ежедневно буду напоминать о приеме {drug_name}, жди сообщения в {hour}:{minute}, доп. инфа - {instruction}')
                else:
                    bot.send_message(message.chat.id,text=f'Не смог создать напоминание, ошибка точно есть в часе или минуте приема - {i}. Попробуйте написать сообщение заново')
                    bot.register_next_step_handler(message, create_remind, k)
            #было бы славно добавить кнопки типо проверьте что верно, если не верно то обратно заново.
        elif k == 'inweek' and len(parts) == 4:
            drug_name = parts[0]  # Анальгин
            weekday = parts[1].split(',') # ['Понедельник', 'Пятница']
            times = parts[2].split(',')  # ['10:00', '11:00']
            instruction = parts[3]  # По две таблетки, запивая водой
            # api_create_remind(message.chat.id,k,drug_name,times,instruction, weekday)
            for day_name in weekday:
                temp=day_name.lower().replace(' ', '')
                day_number = WEEKDAYNUMBER.get(f'{temp}')
                if day_number is None:
                    bot.send_message(message.chat.id,text=f'Не смог создать напоминание, ошибка точно есть в написании дня недели - {day_name}. Попробуйте написать сообщение для этого дня недели заново.')
                    bot.register_next_step_handler(message, create_remind, k)
                else:
                    for i in times:
                        time_parts = i.split(':')   #делаем время на часы и минуты
                        if len(time_parts) == 2:
                            hour = int(time_parts[0])
                            if hour > 24 or hour < 0:
                                bot.send_message(message.chat.id,text=f'Не смог создать напоминание, ошибка точно есть в часе приема - {i}. Попробуйте написать сообщение заново')
                                bot.register_next_step_handler(message, create_remind, k)
                            else:    
                                minute = int(time_parts[1])
                                if minute > 59 or minute < 0:
                                    bot.send_message(message.chat.id,text=f'Не смог создать напоминание, ошибка точно есть в минутах приема - {i}. Попробуйте написать сообщение заново')
                                    bot.register_next_step_handler(message, create_remind, k)
                                else:
                                    requests.post(f'{BASE_URL}', json={"chat":f"{message.chat.id}",'hour':f'{hour}','minute':f'{minute}','med':f'{drug_name}','add':f'{instruction}','day':f'{day_number}'})
                                    response = (requests.get(f'{BASE_URL}?chat={message.chat.id}')).json()
                                    id_last_user_remind = (response[-1]).get('id') #берем ток id
                                    start_remind(message.chat.id,drug_name,hour,minute,instruction,id_last_user_remind,k,day_number)
                                    minute= f'0{minute}' if minute < 10 else minute
                                    hour = f'0{hour}' if hour < 10 else hour
                                    bot.send_message(message.chat.id, text=f'Запомнил!В {day_name} буду напоминать о приеме {drug_name}, жди сообщения в {hour}:{minute}, доп. инфа - {instruction}')
                        else:
                            message = bot.send_message(message.chat.id,text=f'Не смог создать напоминание, ошибка точно есть в часе или минуте приема - {times}. Попробуйте написать сообщение заново')
                            bot.register_next_step_handler(message, create_remind, k)
        else:
            send_message(message, ' Что-то пошло не так, попробуйте заново написать сообщение, свертесь с примером')
            bot.register_next_step_handler(message, create_remind, k)
    #закончил тут

# def api_create_remind(username,k,drug_name,times,intruction, weekday):
#     if k == 'everyday':
#         for i in times:
#             time_parts = i.split(':')   #делаем время на часы и минуты
#             if len(time_parts) == 2:
#                 hour = int(time_parts[0])
#                 print(hour)
#                 if hour > 24 or hour < 0:
#                     bot.send_message(username,text='Не смог создать напоминание, ошибка точно есть в часе приема. Попробуйте написать сообщение заново')
#                     bot.register_next_step_handler(message,create_remind, k)
#                 else:
#                     minute = int(time_parts[1])
#                     # if minute > 59 or minute < 0:
#                     #         message = bot.send_message(username,text='Не смог создать напоминание, ошибка точно есть в минутах приема. Попробуйте написать сообщение заново')
#                     #         bot.register_next_step_handler(message, create_remind, k)
#                     requests.post(f'{BASE_URL}', json={"chat":f"{username}",'hour':f'{hour}','minute':f'{minute}','med':f'{drug_name}','add':f'{intruction}'}) #добавляем в БД напоминалку
#                     print(f'{username} отправил в Бд напоминалку')
#                     response = (requests.get(f'{BASE_URL}?chat={username}')).json() #берем ее обратно, но уже с id
#                     id_last_user_remind = (response[-1]).get('id') #берем ток id
#                     start_remind(username,drug_name,hour,minute,intruction,id_last_user_remind,k, day_number=0)
#             else:
#                 bot.send_message(username,text='Не смог создать напоминание, ошибка точно есть в часе или минуте приема. Попробуйте написать сообщение заново')
#                 bot.register_next_step_handler(message, create_remind, k)
#     if k == 'inweek':
        # for day_name in weekday:
        #     temp=day_name.lower().replace(' ', '')
        #     day_number = WEEKDAYNUMBER.get(f'{temp}')
        #     if day_number is None:
        #         message = bot.send_message(username,text='Не смог создать напоминание, ошибка точно есть в написании дня недели. Попробуйте написать сообщение заново')
        #         bot.register_next_step_handler(message, create_remind, k)
        #     for i in times:
        #         time_parts = i.split(':')   #делаем время на часы и минуты
        #         if len(time_parts) == 2:
        #             hour = int(time_parts[0])
        #             # if hour > 24 or hour < 0:
        #             #     message = bot.send_message(username,text='Не смог создать напоминание, ошибка точно есть в часе приема. Попробуйте написать сообщение заново')
        #             #     bot.register_next_step_handler(message, create_remind, k)
        #             minute = int(time_parts[1])
        #             # if minute > 59 or minute < 0:
        #             #     message = bot.send_message(username,text='Не смог создать напоминание, ошибка точно есть в минутах приема. Попробуйте написать сообщение заново')
        #             #     bot.register_next_step_handler(message, create_remind, k)
        #             requests.post(f'{BASE_URL}', json={"chat":f"{username}",'hour':f'{hour}','minute':f'{minute}','med':f'{drug_name}','add':f'{intruction}','day':f'{day_number}'})
        #             response = (requests.get(f'{BASE_URL}?chat={username}')).json()
        #             id_last_user_remind = (response[-1]).get('id') #берем ток id
        #             start_remind(username,drug_name,hour,minute,intruction,id_last_user_remind,k,day_number)
        #         else:
        #             message = bot.send_message(username,text='Не смог создать напоминание, ошибка точно есть в часе или минуте приема. Попробуйте написать сообщение заново')
        #             bot.register_next_step_handler(message, create_remind, k)

def start_remind(username,drug_name,hour,minute,intruction,id_last_user_remind,k,day_number):
    if k == 'everyday':
        background_scheduler.add_job(send_remind, 'cron',hour=hour, minute=minute, id=str(id_last_user_remind), args=(username,drug_name,intruction))
    elif k == 'inweek':
        background_scheduler.add_job(send_remind, 'cron', day_of_week=day_number, hour=hour, minute=minute, id=str(id_last_user_remind), args=(username,drug_name,intruction))

def api_list_remind(message):
    response = (requests.get(f'{BASE_URL}?chat={message.chat.id}')).json()
    if not response:
        bot.send_message(message.chat.id,text='У вас еще нет напоминаний, самое время их создать!')
    mes = {}
    for i in response:
        id = i.get('id')
        day = i.get('day')
        if day != 10:        
            day_name = 'в ' + str([i for i in WEEKDAYNUMBER.keys()].pop(day))
        else:
            day_name='ежедневно'
        hour = i.get('hour')
        hour = f'0{hour}' if hour < 10 else hour
        minute =i.get('minute')
        minute= f'0{minute}' if minute < 10 else minute
        med = i.get('med')
        add = i.get('add')
        print(f'Вы принимаете {day_name} в {hour}:{minute} {med}, доп инфа: {add}{id}')
        mes.update({f'Вы принимаете {day_name} в {hour}:{minute} {med}, доп инфа: {add}\n':f'{id}'})
    # print(mes)
    return mes

def api_delete(message, id):
    T = check_main_command(message)
    if T is False:
        if message.text.isdigit():
            response = requests.delete(f'{BASE_URL}', json={'id':f'{message.text}'})
            print(response.json())
            if response.json() == 200:
                bot.send_message(message.chat.id, text=f'Повезло, вроде реально удалилось!')
                background_scheduler.remove_job(f'{message.text}')

            else:
                bot.send_message(message.chat.id, text=f'Кажется вы промахнулись по клавиатуре, попробуйте еще раз')
                bot.register_next_step_handler(message, api_delete, id)

        else:
            bot.send_message(message.chat.id, protect_content = True, text=f'Так как это не цифра, бот выдал ошибку, попробуем еще раз.')
            bot.register_next_step_handler(message, api_delete, id)


def send_remind(username,drug_name,intruction):
    bot.send_message(username, text=f'Тук-тук!!! Пора принять "{drug_name}", ваша дополнительная информация:"{intruction}"')

def send_message(message,text):
    bot.send_message(message.chat.id, text = text)

def check_main_command(message):
    if message.text in MAIN_COMMAND:
        bot.send_message(message.chat.id,text=f'Понял, понял меняем тактику. Перенаправляю на {message.text}')
        distribution(message)
    else:
        return False

try:
    bot.polling(none_stop=True)

except ConnectionError as e:
    print('Ошибка соединения: ', e)
except Exception as r:
    print("Непридвиденная ошибка: ", r)
finally:
    print("Здесь всё закончилось")