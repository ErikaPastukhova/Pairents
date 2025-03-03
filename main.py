import profile

import telebot
import os
from dotenv import load_dotenv
from telebot import types

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

profiles = dict()

welcome_message = ('Добро пожаловать в Pairents - сервис для дружеского знакомство молодых родителей c системой мэтчинга, основывающейся на схожих взглядах на воспитание детей! Нажмите, чтобы продолжить.')

# реакция бота на команду \start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) # создает сетку для кнопок
    btn1 = types.KeyboardButton("Продолжить") #какая кнопка будет у пользователя
    markup.add(btn1)
    bot.send_message(message.from_user.id, welcome_message, reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == 'Продолжить':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Заполнить анкету')
        btn2 = types.KeyboardButton('У меня уже есть анкета')
        # btn3 = types.KeyboardButton('Советы по оформлению публикации')
        # markup.add(btn1, btn2, btn3)
        markup.add(btn1, btn2)
        bot.send_message(message.from_user.id, 'Выберите нужное', reply_markup=markup) #ответ бота

    if message.text == 'Заполнить анкету':
        person = profile.Profile()
        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        # btn1 = types.KeyboardButton('Ввести имя')
        # btn2 = types.KeyboardButton('Ввести фамилию')
        # btn3 = types.KeyboardButton('')
        # markup.add(btn1, btn2, btn3)
        # markup.add(btn1, btn2)
        bot.send_message(message.from_user.id, 'Введите свое имя') #ответ бота
        person.name = message.text
        print(person.name)



bot.polling(none_stop=True, interval=0)  # обязательная для работы бота часть