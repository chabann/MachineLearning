import telebot
from telebot import types
from reviews import Reviews
from predict_mood import get_prediction

f = open('token.txt', 'r')
token = f.read()
bot = telebot.TeleBot(token)

##старт бота##
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, введи название фильма!', reply_markup=types.ReplyKeyboardRemove())

##остановка бота##
@bot.message_handler(commands=['stop'])
def stop(message):
    startKBoard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    Start = types.KeyboardButton(text='Старт')
    startKBoard.add(Start)

    bot.send_message(message.chat.id, 'Поиск окончен', reply_markup=startKBoard)

##Инициализация поиска##
@bot.message_handler(func=lambda message: message.text != '')
def search_film(message):
    if message.text == 'Завершить':
        stop(message)
    elif message.text == 'Старт':
        start(message)
    else:
        ar_films = Reviews(message.text).process_search()

        if not len(ar_films):
            startKBoard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            Stop = types.KeyboardButton(text='Завершить')
            startKBoard.add(Stop)
            bot.send_message(message.chat.id, 'По данному запросу результатов не найдено',
                             reply_markup=startKBoard)
        elif len(ar_films) == 1:
            startKBoard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            Choose = types.KeyboardButton(text='Выбрать')
            Stop = types.KeyboardButton(text='Завершить')
            startKBoard.add(Choose, Stop)

            answer = ar_films[0]['name'] + '. ' + ar_films[0]['date'] + '. ' + ar_films[0]['description']
            sent = bot.send_message(message.chat.id, answer)
            bot.register_next_step_handler(sent, print_film, {'films': ar_films, 'i': 1})

            bot.send_message(message.chat.id, 'Это единственный найденный фильм по данному запросу, нажми кнопку '
                                              'Выбрать, '
                                              'чтобы получить по нему отзывы либо перефразируй запрос',
                             reply_markup=startKBoard)
        else:
            startKBoard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            Next = types.KeyboardButton(text='Дальше')
            Back = types.KeyboardButton(text='Назад')
            Choose = types.KeyboardButton(text='Выбрать')
            Stop = types.KeyboardButton(text='Завершить')
            startKBoard.add(Next, Back, Choose, Stop)

            bot.send_message(message.chat.id, 'Используй кнопки, чтобы выбрать нужный фильм',
                             reply_markup=startKBoard)

            message.text = 'Дальше'
            print_film(message, {'films': ar_films, 'i': 0})

##Вывод результатов##
def print_film(message, films):
    startKBoard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    Stop = types.KeyboardButton(text='Завершить')
    startKBoard.add(Stop)

    startKBoardLast = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    Stop = types.KeyboardButton(text='Завершить')
    Choose = types.KeyboardButton(text='Выбрать')
    startKBoardLast.add(Choose, Stop)

    if message.text == 'Назад':
        print(films['i'] - 1, len(films['films']))
        if films['i'] - 1 > -1:
            film = films['films'][films['i'] - 1]
            answer = film['name'] + '. ' + film['date'] + '. ' + film['description']
            sent = bot.send_message(message.chat.id, answer)
            bot.register_next_step_handler(sent, print_film, {'films': films['films'], 'i': films['i'] - 1})
        else:
            bot.send_message(message.chat.id, 'Это первый найденый фильм в списке', reply_markup=startKBoardLast)

    elif message.text == 'Дальше':
        if films['i'] < len(films['films']):
            film = films['films'][films['i']]
            answer = film['name'] + '. ' + film['date'] + '. ' + film['description']
            sent = bot.send_message(message.chat.id, answer)

            if films['i'] + 1 < len(films['films']):
                bot.register_next_step_handler(sent, print_film, {'films': films['films'], 'i': films['i'] + 1})
            else:
                bot.register_next_step_handler(sent, print_film, {'films': films['films'], 'i': films['i'] + 1})
                bot.send_message(message.chat.id, 'Это последний из найденных фильмов',
                                 reply_markup=startKBoardLast)
        else:
            bot.send_message(message.chat.id, 'Это все найденные фильмы, пожалуйста, перефразируй запрос',
                             reply_markup=startKBoard)

    elif message.text == 'Выбрать':
        film = films['films'][films['i'] - 1]
        answer = film['name'] + '. ' + film['date']

        bot.send_message(message.chat.id, 'Выбранный фильм: ' + answer, reply_markup=types.ReplyKeyboardRemove())

        reviews_info = Reviews(film['name']).get_reviews_info(film['link'])
        ar_reviews = reviews_info['arReviews']
        if not ar_reviews:
            bot.send_message(message.chat.id, 'У данного фильма нет отзывов, выбери другой',
                             reply_markup=startKBoard)
        else:
            if len(ar_reviews) % 10 == 1:
                mess_count = 'У данного фильма ' + str(len(ar_reviews)) + ' отзыв'
            elif (len(ar_reviews) % 10 == 2) or (len(ar_reviews) % 10 == 3) or (len(ar_reviews) % 10 == 4):
                mess_count = 'У данного фильма ' + str(len(ar_reviews)) + ' отзыва'
            else:
                mess_count = 'У данного фильма ' + str(len(ar_reviews)) + ' отзывов'

            bot.send_message(message.chat.id, mess_count)
            bot.send_message(message.chat.id, 'Оценка фильма зрителями на Metacritic: ' +
                             str(reviews_info['averageScore']))
            bot.send_message(message.chat.id, get_prediction(ar_reviews))
            bot.send_message(message.chat.id, 'Введи название следующего фильма или нажми Завершить',
                             reply_markup=startKBoard)

    elif message.text == 'Завершить':
        stop(message)
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю, воспользуйся кнопками')


bot.polling()