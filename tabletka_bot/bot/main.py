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

@bot.message_handler(commands=['start'])
def welcome(message):
    
    # registrate(message.chat.id)#тут регаю чела в джанго, если первый раз зашел, то регается по chat id, если не первый то будет 404 и идет дальше
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item3 = types.KeyboardButton("Создание напоминания приема медикоментов")
    item2 = types.KeyboardButton("Просмотр напоминания приема медикоментов")
    item1 = types.KeyboardButton('/start')

    keyboard.add(item1, item2, item3)
    bot.send_message(message.chat.id, reply_markup = keyboard, protect_content = True, text ="1-я чтобы попробовать начать сначала.\n." 
                                                                                                                 "\n3-я кнопка для индетификации")
    
@bot.message_handler(content_types=["text"])
def distribution(message):
    if message.text == 'Создание напоминания приема медикоментов':
        pass
    # background_scheduler.add_job(send_message, 'cron', second=2, id='foo', args=(message,))

def send_message(message):
    print()
    bot.send_message(message.chat.id, text='опа')

try:
    bot.polling(none_stop=True)

except ConnectionError as e:
    print('Ошибка соединения: ', e)
except Exception as r:
    print("Непридвиденная ошибка: ", r)
finally:
    print("Здесь всё закончилось")