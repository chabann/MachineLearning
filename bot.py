import telebot
from telebot import types
import datetime
from reviews import Reviews

f = open('token.txt', 'r')
token = f.read()
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, введите название фильма!')


@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, 'Поиск окончен')


@bot.message_handler(func=lambda message: message.text != '')
def search_film(message):
    ar_films = Reviews(message.text).process_search()

    if not len(ar_films):
        bot.send_message(message.chat.id, 'По данному запросу результатов не найдено')
    else:
        startKBoard = types.ReplyKeyboardMarkup(row_width=1)
        Next = types.KeyboardButton(text="Дальше")
        Choose = types.KeyboardButton(text="Выбрать")
        startKBoard.add(Next, Choose)

        sent = bot.send_message(message.chat.id, 'Используйте кнопки, чтобы выбрать нужный фильм', reply_markup=startKBoard)
        bot.register_next_step_handler(sent, print_film, {'films': ar_films, 'i': 0})


def print_film(message, films):
    if message.text == 'Дальше':
        film = films['films'][films['i']]
        answer = film['name'] + '. ' + film['date'] + '. ' + film['description']
        sent = bot.send_message(message.chat.id, answer)

        if films['films'][films['i'] + 1] is not None:
            bot.register_next_step_handler(sent, print_film, {'films': films['films'], 'i': films['i'] + 1})
        else:
            bot.send_message(message.chat.id, 'Это все найденные фильмы, пожалуйста, перефразируйте запрос')
    elif message.text == 'Выбрать':
        film = films['films'][films['i'] - 1]
        answer = film['name'] + '. ' + film['date']
        bot.send_message(message.chat.id, 'Выбранный фильм: ' + answer)


bot.polling()
