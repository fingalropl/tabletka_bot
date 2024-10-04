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

from CONTANS import WEEKDAYNUMBER, BASE_URL

def dynamic_import(module):
    return importlib.import_module(module)
#загрузка констант
load_dotenv()   
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
item3 = types.KeyboardButton("Создание напоминания  ")
item2 = types.KeyboardButton("Просмотр напоминания приема ")
item1 = types.KeyboardButton('/start')
keyboard.add(item1, item2, item3)
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, reply_markup = keyboard, protect_content = True, text ="1-я чтобы попробовать начать сначала.\n." 
                                                                                                                 "\n3-я кнопка для индетификации")
    
@bot.message_handler(content_types=["text"])
def distribution(message):
    if message.text == 'Создание напоминания':
        bot.send_message(message.chat.id, text='Выберите периодичность приема лекарства:', reply_markup=inline1)

@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'everyday':
        message=bot.send_message(call.message.chat.id, text='Напишите сообщение в формате: \n"Название медикомента; время приемов; дополнительная информация"\nПример: "Анальгин; 10:00, 11:00; По две таблетки, запивая водой"')
        bot.register_next_step_handler(message, create_remind, call.data)
    elif call.data == 'inweek':
       message=bot.send_message(call.message.chat.id, text='Напишите сообщение в формате: \n"Название медикомента; Дни недели приема; время приемов; дополнительная информация"\nПример: "Анальгин; Понедельник, Пятница; 10:00, 11:00; По две таблетки, запивая водой"')
       bot.register_next_step_handler(message, create_remind, call.data)

def create_remind(message,k):
    parts = message.text.split(';')
    if k == 'everyday' and len(parts) == 3:
        drug_name = parts[0]  # Анальгин
        times = parts[1].split(',')  # ['10:00', '11:00']
        instruction = parts[2]  # По две таблетки, запивая водой
        api_create_remind(message.chat.id,k,drug_name,times,instruction, weekday = 0)
        bot.send_message(message.chat.id, text=f'Название препарата-{drug_name}, время приема - {times}, доп. информация - {instruction}')
        #было бы славно добавить кнопки типо проверьте что верно, если не верно то обратно заново.
    elif k == 'inweek' and len(parts) == 4:
        drug_name = parts[0]  # Анальгин
        weekday = parts[1].split(',') # ['Понедельник', 'Пятница']
        times = parts[2].split(',')  # ['10:00', '11:00']
        instruction = parts[3]  # По две таблетки, запивая водой
        api_create_remind(message.chat.id,k,drug_name,times,instruction, weekday)
    else:
        send_message(message, ' Что-то пошло не так, попробуйте заново написать сообщение, свертесь с примером')
        bot.register_next_step_handler(message, create_remind, k)
    #закончил тут

def api_create_remind(username,k,drug_name,times,intruction, weekday):
    if k == 'everyday':
        for i in times:
            time_parts = i.split(':')   #делаем время на часы и минуты
            hour = int(time_parts[0]) 
            minute = int(time_parts[1])
            requests.post(f'{BASE_URL}', json={"chat":f"{username}",'hour':f'{hour}','minute':f'{minute}','med':f'{drug_name}','add':f'{intruction}'}) #добавляем в БД напоминалку
            print(f'{username} отправил в Бд напоминалку')
            response = (requests.get(f'{BASE_URL}?chat={username}')).json() #берем ее обратно, но уже с id
            id_last_user_remind = (response[-1]).get('id') #берем ток id
            start_remind(username,drug_name,hour,minute,intruction,id_last_user_remind,k, day_number=0)
    if k == 'inweek':
        #остановился тут, вроде все работает. 
        for day_name in weekday:
            temp=day_name.lower().replace(' ', '')
            day_number = WEEKDAYNUMBER.get(f'{temp}')
            for i in times:
                time_parts = i.split(':')   #делаем время на часы и минуты
                hour = int(time_parts[0]) 
                minute = int(time_parts[1])
                requests.post(f'{BASE_URL}', json={"chat":f"{username}",'hour':f'{hour}','minute':f'{minute}','med':f'{drug_name}','add':f'{intruction}','day':f'{day_number}'})
                response = (requests.get(f'{BASE_URL}?chat={username}')).json()
                id_last_user_remind = (response[-1]).get('id') #берем ток id
                start_remind(username,drug_name,hour,minute,intruction,id_last_user_remind,k,day_number)
def start_remind(username,drug_name,hour,minute,intruction,id_last_user_remind,k,day_number):
    if k == 'everyday':
        background_scheduler.add_job(send_remind, 'cron',hour=hour, minute=minute, id=str(id_last_user_remind), args=(username,drug_name,intruction))
    elif k == 'inweek':
        background_scheduler.add_job(send_remind, 'cron', day_of_week=day_number, hour=hour, minute=minute, id=str(id_last_user_remind), args=(username,drug_name,intruction))


def send_remind(username,drug_name,intruction):
    bot.send_message(username, text=f'Пора принять "{drug_name}", твоя дополнительная информация:"{intruction}"')

def send_message(message,text):
    bot.send_message(message.chat.id, text = text)

try:
    bot.polling(none_stop=True)

except ConnectionError as e:
    print('Ошибка соединения: ', e)
except Exception as r:
    print("Непридвиденная ошибка: ", r)
finally:
    print("Здесь всё закончилось")