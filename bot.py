import telebot
import datetime
from reviews import Reviews


f = open('token.txt', 'r')
token = f.read()
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Введите название фильма.')

@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, 'Поиск окончен')

@bot.message_handler(func = lambda message: message.text != '')
def search_film(message):
    Test = Reviews(message.text)


bot.polling()
