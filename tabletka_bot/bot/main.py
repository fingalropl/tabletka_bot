import os
import requests
import telebot 
from telebot import types 
from dotenv import load_dotenv
import datetime as dt
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()   

TG_TOKEN = os.getenv('TG_TOKEN')
background_scheduler  = BackgroundScheduler()
background_scheduler.start()

bot = telebot.TeleBot(TG_TOKEN)
# bot.scheduler = background_scheduler
inline1 = types.InlineKeyboardMarkup()
ik = types.InlineKeyboardButton(text = 'Ежедневно', callback_data = 'everyday')
ik2 = types.InlineKeyboardButton(text = 'По определенным дням недели', callback_data = 'inweek')
# ik3 = types.InlineKeyboardButton()
inline1.add(ik,ik2)


@bot.message_handler(commands=['start'])
def welcome(message):
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item3 = types.KeyboardButton("Создание напоминания  ")
    item2 = types.KeyboardButton("Просмотр напоминания приема ")
    item1 = types.KeyboardButton('/start')

    keyboard.add(item1, item2, item3)
    bot.send_message(message.chat.id, reply_markup = keyboard, protect_content = True, text ="1-я чтобы попробовать начать сначала.\n." 
                                                                                                                 "\n3-я кнопка для индетификации")
    
@bot.message_handler(content_types=["text"])
def distribution(message):
    if message.text == 'Создание напоминания':
        bot.send_message(message.chat.id, text='Выберите периодичность приема лекарства:', reply_markup=inline1)
        # create_remind(message)

@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    print('1')
    if call.data == 'everyday':
        message=bot.send_message(call.message.chat.id, text='Напишите сообщение в формате: \n"Название медикомента; кол-во приемов в день; время приемов; дополнительная информация"\nПример: "Анальгин; 2; 10:00, 11:00; По две таблетки, запивая водой"')
        print('2')
        bot.register_next_step_handler(message, create_remind, call.data)
        print('3')

    elif call.data == 'inweek':
        pass

def create_remind(message,k):
    if k == 'everyday':
        # api_create_remind(message)
        parts = message.text.split(';')
        drug_name = parts[0]  # Анальгин
        dose = int(parts[1])  # 2
        times = parts[2].split(',')  # ['10:00', '11:00']
        instruction = parts[3]  # По две таблетки, запивая водой
        bot.send_message(message.chat.id, text=f'Название препарата-{drug_name}, кол-во приемов в день - {dose}, время приема - {times}, доп. информация - {instruction}')
        background_scheduler.add_job(send_message, 'cron', second=2, id='foo', args=(message,))
    elif k == 'inweek':
        pass
    #закончил тут
        

def send_message(message):
    bot.send_message(message.chat.id, text='опа')

try:
    bot.polling(none_stop=True)

except ConnectionError as e:
    print('Ошибка соединения: ', e)
except Exception as r:
    print("Непридвиденная ошибка: ", r)
finally:
    print("Здесь всё закончилось")