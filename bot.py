import telebot
from telebot import types
import datetime
from reviews import Reviews

f = open('token.txt', 'r')
token = f.read()
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, введи название фильма!')


@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, 'Поиск окончен', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(func=lambda message: message.text != '')
def search_film(message):
    if message.text == 'Завершить':
        stop(message)

    ar_films = Reviews(message.text).process_search()

    if not len(ar_films):
        startKBoard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        Stop = types.KeyboardButton(text='Завершить')
        startKBoard.add(Stop)
        bot.send_message(message.chat.id, 'По данному запросу результатов не найдено',
                         reply_markup=startKBoard)
    else:
        startKBoard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        Next = types.KeyboardButton(text='Дальше')
        Choose = types.KeyboardButton(text='Выбрать')
        Stop = types.KeyboardButton(text='Завершить')
        startKBoard.add(Next, Choose, Stop)

        bot.send_message(message.chat.id, 'Используй кнопки, чтобы выбрать нужный фильм',
                         reply_markup=startKBoard)

        message.text = 'Дальше'
        print_film(message, {'films': ar_films, 'i': 0})


def print_film(message, films):
    if message.text == 'Дальше':
        film = films['films'][films['i']]
        answer = film['name'] + '. ' + film['date'] + '. ' + film['description']
        sent = bot.send_message(message.chat.id, answer)

        if films['i'] + 1 < len(films['films']):
            bot.register_next_step_handler(sent, print_film, {'films': films['films'], 'i': films['i'] + 1})
        else:
            bot.send_message(message.chat.id, 'Это все найденные фильмы, пожалуйста, перефразируй запрос',
                             reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'Выбрать':
        film = films['films'][films['i'] - 1]
        answer = film['name'] + '. ' + film['date']

        startKBoard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        Stop = types.KeyboardButton(text='/stop')
        startKBoard.add(Stop)

        bot.send_message(message.chat.id, 'Выбранный фильм: ' + answer, reply_markup=startKBoard)

        ar_reviews = Reviews(film['name']).get_reviews(film['link'])
        if not ar_reviews:
            bot.send_message(message.chat.id, 'Данный фильм не содержит отзывов, выбери другой')
        else:
            bot.send_message(message.chat.id, 'У данного фильма ' + str(len(ar_reviews)) + ' отзывов')

    elif message.text == 'Завершить':
        stop(message)
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю, воспользуйся кнопками')


bot.polling()
