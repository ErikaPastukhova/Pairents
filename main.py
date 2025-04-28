import matching
from profiles import add_profile, get_profile, update_profile, remove_profile, profile_as_text
from profiles import Profile, Child, Sex
import profiles
from matching import get_next_candidate, like_candidate, skip_candidate, reject_candidate

from psycho_test_results import add_psycho_test, get_psycho_test, update_psycho_test, remove_psycho_test, get_result_message
from psycho_test_results import MALE_QUESTIONS, FEMALE_QUESTIONS, PsychoTestResult
import psycho_test_results

import cities

import telebot
import os
import re
from dotenv import load_dotenv
from telebot import types

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

welcome_message = ('''Добро пожаловать в PAIRENTS!

Pairents - это сервис для дружеского знакомство молодых родителей c системой мэтчинга, которая основыввается на схожих взглядах на воспитание детей!

Дети - это прекрасно, однако все мы люди и сталкиваемся с различными труднеостями на этом пути. Pairents - это не только про дружеский дейтинг, но и про поддерживающее сообщество родитетелей, которые готовы прийти на помочь в трудную минуту, поддержать морально и физически.

В боте доступны следующие команды:
/help - показать список доступных команд
/start - начать с начала
/create_profile - создать или обновить профиль
/view_profile - посмотреть свой профиль
/delete_profile - удалить свой профиль
/search - начать поиск собеседников

Возрастное ограничение сервиса: 16+.

Сейчас сервис работает в 16 городах России: Москва, Санкт-Петербург, Новосибирск, Екатеринбург, Казань, Красноярск, Нижний Новгород, Челябинск, Самара, Уфа, Ростов-на-Дону, Краснодар, Омск, Воронеж, Пермь, Волгоград.
    
Команда Pairents всегда рада и открыта к новым идеям и предложениям. Если Вы обнаружили ошибку в работе сервиса, или Вашего города нет в списке, и по любым другим вопросам можно обратиться к Эрике @ekhuf.

Надеемся, что наш сервис станет помощником для Вас, а Вы найдете здесь чутких и понимающих друзей.

Нажмите, чтобы продолжить.''')


def is_valid_name(name: str) -> bool:
    if not name:
        return False

    if not name[0].isupper():
        return False

    russian_pattern = r'^[А-ЯЁа-яё\- ]+$'
    english_pattern = r'^[A-Za-z\- ]+$'

    if re.match(russian_pattern, name):
        return True
    elif re.match(english_pattern, name):
        return True
    else:
        return False


# реакция бота на команду \start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создает сетку для кнопок
    btn1 = types.KeyboardButton("Продолжить")  # какая кнопка будет у пользователя
    markup.add(btn1)
    bot.send_message(message.from_user.id, welcome_message, reply_markup=markup)


@bot.message_handler(commands=['search'])
def search(message):
    user_id = message.chat.id
    candidate_id = get_next_candidate(user_id)
    if candidate_id is None:
        bot.send_message(user_id, "Пока нет подходящих анкет. Попробуй позже.")
        return

    candidate = get_profile(candidate_id)

    if candidate is None:
        bot.send_message(user_id, "Произошла mistake & misunderstanding. Попробуй позже.")
        return

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton("❤️", callback_data=f"like_{candidate_id}"),
        telebot.types.InlineKeyboardButton("🤔 Отложить", callback_data=f"skip_{candidate_id}"),
        telebot.types.InlineKeyboardButton("❌", callback_data=f"reject_{candidate_id}")
    )

    response, photo = profile_as_text(candidate)

    if photo:
        bot.send_photo(user_id, photo, caption=response, reply_markup=keyboard)
    else:
        response += "Фотография не загружена."
        bot.send_message(user_id, response, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith(('like_', 'skip_', 'reject_')))
def callback_handler(call):
    user_id = call.from_user.id
    action, target_id = call.data.split('_')
    target_id = int(target_id)

    if action == 'like':
        like_candidate(user_id, target_id, bot)
        bot.answer_callback_query(call.id, "Интерес проявлен!")
    elif action == 'skip':
        skip_candidate(user_id, target_id)
        bot.answer_callback_query(call.id, "Анкета пропущена.")
    elif action == 'reject':
        reject_candidate(user_id, target_id)
        bot.answer_callback_query(call.id, "Анкета отклонена.")

    search(call.message)


@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = "Список доступных команд:\n" \
                   "/start - начать сначала:\n" \
                   "/help - показать данное сообщение\n" \
                   "/create_profile - создать или обновить профиль\n" \
                   "/view_profile - посмотреть свой профиль\n" \
                   "/delete_profile - удалить свой профиль\n" \
                   "/search - начать поиск"
    bot.send_message(message.chat.id, help_message)


# @bot.message_handler(commands=['photo_id'])
# def send_help(message):
#     bot.send_message(message.chat.id, "Пришли фото")
#     bot.register_next_step_handler(message, send_file_id)
#
# def send_file_id(message):
#     bot.send_message(message.chat.id, message.photo[-1].file_id)

@bot.message_handler(commands=['view_profile'])
def view_profile(message):
    tg_id = message.chat.id
    profile = get_profile(tg_id)
    if profile:
        response, photo = profile_as_text(profile)
        if photo:
            bot.send_photo(tg_id, photo, caption=response)
        else:
            response += "Фотография не загружена."
            bot.send_message(tg_id, response)
    else:
        bot.send_message(tg_id,
                         "Ваш профиль не найден. Пожалуйста, создайте профиль с помощью команды /create_profile.")


@bot.message_handler(commands=['create_profile'])
def create_profile(message):
    tg_id = message.chat.id
    profile = get_profile(tg_id)
    if not profile:
        profile = Profile()
        add_profile(tg_id, profile)
    bot.send_message(tg_id, "Пожалуйста, введите ваше имя:", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_name_step, profile)


@bot.message_handler(commands=['delete_profile'])
def delete_profile(message):
    tg_id = message.chat.id
    profile = get_profile(tg_id)
    if profile:
        remove_profile(tg_id)
        remove_psycho_test(tg_id)
        bot.send_message(tg_id, "Ваш профиль успешно удалён.")
    else:
        bot.send_message(tg_id, "Ваш профиль не найден.")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Продолжить':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок
        btn1 = types.KeyboardButton('Заполнить анкету')
        btn2 = types.KeyboardButton('У меня уже есть анкета')
        # btn3 = types.KeyboardButton('Советы по оформлению публикации')
        # markup.add(btn1, btn2, btn3)
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, 'Выберите нужное. Если у вас уже была анкета, но вы нажмете "Заполнить анкету" - старая анкета будет удалена', reply_markup=markup)  # ответ бота

    if message.text == 'Заполнить анкету':
        create_profile(message)

    if message.text == 'У меня уже есть анкета':
        if get_profile(message.chat.id) is None:
            bot.send_message(message.chat.id, 'Профиль не найден. Вам нужно сначала заполнить анкету')
            create_profile(message)
        else:
            bot.send_message(message.chat.id, 'Введите команду /search, чтобы начать поиск собеседников', reply_markup=telebot.types.ReplyKeyboardRemove())


def process_name_step(message, profile):
    name = message.text
    if not is_valid_name(name):
        response = """Имя должно начинаться с заглавной буквы. Буквы имени должны быть или все русскими, или все английскими. Разрешены знаки пробела и дефиса. Пожалуйста, введите свое имя еще раз в корректном формате. 

Если Вы считаете, что произошла ошибка, напишите Эрике @ekhuf"""
        bot.send_message(message.chat.id, response)
        bot.register_next_step_handler(message, process_name_step, profile)
        return
    profile.name = name
    bot.send_message(message.chat.id, "Теперь введите вашу фамилию:")
    bot.register_next_step_handler(message, process_surname_step, profile)


def process_surname_step(message, profile):
    surname = message.text
    if not is_valid_name(surname):
        response = """Фамилия должна начинаться с заглавной буквы. Буквы имени должны быть или все русскими, или все английскими. Разрешены знаки пробела и дефиса. Пожалуйста, введите свою фамилию еще раз в корректном формате. 

Если Вы считаете, что произошла ошибка, напишите Эрике @ekhuf"""
        bot.send_message(message.chat.id, response)
        bot.register_next_step_handler(message, process_surname_step, profile)
        return
    profile.surname = surname
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Мужской', 'Женский')
    bot.send_message(message.chat.id, "Выберите ваш пол:", reply_markup=keyboard)
    bot.register_next_step_handler(message, process_sex_step, profile)


def process_sex_step(message, profile):
    profile.sex = Sex.MALE if message.text == 'Мужской' else Sex.FEMALE if message.text == 'Женский' else None
    if profile.sex is None:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('Мужской', 'Женский')
        bot.send_message(message.chat.id, "Пол некорректен. Выберите ваш пол из предложенных:", reply_markup=keyboard)
        bot.register_next_step_handler(message, process_sex_step, profile)
        return
    bot.send_message(message.chat.id, "Введите, сколько Вам полных лет:", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_age_step, profile)


def process_age_step(message, profile):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Возраст должен быть целым положительным числом. Повторно введите, сколько Вам полных лет:")
        bot.register_next_step_handler(message, process_age_step, profile)
        return
    profile.age = int(message.text)
    if profile.age < 16:
        bot.send_message(message.chat.id, "Наш сервис 16+. Введите ваш правдивый возраст.")
        bot.register_next_step_handler(message, process_age_step, profile)
        return
    bot.send_message(message.chat.id, '''Введите город Вашего проживания

На данный момент сервис работает в следующих городах:
Москва
Санкт-Петербург
Новосибирск
Екатеринбург
Казань
Красноярск
Нижний Новгород
Челябинск
Самара
Уфа
Ростов-на-Дону
Краснодар
Омск
Воронеж
Пермь
Волгоград

Если Вашего города нет в списке - пожалуйста, свяжитесь с Эрикой @ekhuf''')
    bot.register_next_step_handler(message, process_city_step, profile)


def process_city_step(message, profile):
    if message.text not in cities.all_cities.keys():
        bot.send_message(message.chat.id, '''Введите корректное название города или свяжитесь с Эрикой @ekhuf, если Вашего города нет в списке:

Москва
Санкт - Петербург
Новосибирск
Екатеринбург
Казань
Красноярск
Нижний
Новгород
Челябинск
Самара
Уфа
Ростов - на - Дону
Краснодар
Омск
Воронеж
Пермь
Волгоград''')
        bot.register_next_step_handler(message, process_city_step, profile)
        return
    profile.city = message.text
    if profile.city in cities.russian_cities_with_subway.keys():
        request = "Введите ближайшую к Вашему дому станцию метро/МЦД/БКЛ/МЦК."
    else:
        request = "Введите район, в котором Вы проживаете."
    bot.send_message(message.chat.id, request)
    bot.register_next_step_handler(message, process_district_step, profile)


def process_district_step(message, profile):
    if message.text not in cities.all_cities[profile.city].keys():
        city_district_type = "метро" if profile.city in cities.russian_cities_with_subway.keys() else "района"
        bot.send_message(message.chat.id, f"Не нашли такого названия в базе данных, убедитесь в правильности написания {city_district_type}. Если все верно, но ошибка появилась вновь - введите другое название {city_district_type} рядом.")
        bot.register_next_step_handler(message, process_district_step, profile)
        return
    profile.district = message.text
    bot.send_message(message.chat.id, "Загрузите вашу фотографию. Будет здорово, если это будет семейное фото:")
    bot.register_next_step_handler(message, process_photo_step, profile)


def process_photo_step(message, profile):
    if message.photo:
        profile.photo = message.photo[-1].file_id
        bot.send_message(message.chat.id, "Введите количество детей:")
        bot.register_next_step_handler(message, process_num_of_children_step, profile)
    else:
        bot.send_message(message.chat.id, "Ошибка загрузки фотографии. Попробуйте еще раз.")
        bot.register_next_step_handler(message, process_photo_step, profile)


def process_num_of_children_step(message, profile):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Количество детей должно быть числом. Введите количество детей в формате числа:")
        bot.register_next_step_handler(message, process_num_of_children_step, profile)
        return
    profile.num_of_children = int(message.text)
    if profile.num_of_children > 0:
        bot.send_message(message.chat.id, f"Введите информацию о {1}-м ребенке:")
        bot.send_message(message.chat.id, "Имя ребенка:")
        bot.register_next_step_handler(message, process_child_info_step, profile)
    else:
        profile.children.clear()
        update_profile(message.chat.id, profile)
        bot.send_message(message.chat.id, "Ваш профиль успешно создан или обновлен!")
        fill_psycho_test(message, profile.sex)


def process_child_info_step(message, profile):
    child = Child()
    name = message.text
    if not is_valid_name(name):
        response = """Имя должно начинаться с заглавной буквы. Буквы имени должны быть или все русскими, или все английскими. Разрешены знаки пробела и дефиса. Пожалуйста, введите свое имя еще раз в корректном формате. 

    Если Вы считаете, что произошла ошибка, напишите Эрике @ekhuf"""
        bot.send_message(message.chat.id, response)
        bot.register_next_step_handler(message, process_child_info_step, profile)
        return
    child.name = name
    profile.children.append(child)
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Мужской', 'Женский')
    bot.send_message(message.chat.id, "Пол ребенка:", reply_markup=keyboard)
    bot.register_next_step_handler(message, lambda msg, p=profile, c=child: process_child_sex_step(msg, p, c))


def process_child_sex_step(message, profile, child):
    child.sex = Sex.MALE if message.text == 'Мужской' else Sex.FEMALE if message.text == 'Женский' else None
    if child.sex is None:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('Мужской', 'Женский')
        bot.send_message(message.chat.id, "Пол некорректен. Выберите пол из предложенных:", reply_markup=keyboard)
        bot.register_next_step_handler(message, lambda msg, p=profile, c=child: process_child_sex_step(msg, p, c))
        return
    bot.send_message(message.chat.id, "Возраст ребенка:", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, lambda msg, p=profile, c=child: process_child_age_step(msg, p, c))


def process_child_age_step(message, profile, child):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Возраст должен быть числом. Введите возраст в формате числа:")
        bot.register_next_step_handler(message, lambda msg, p=profile, c=child: process_child_age_step(msg, p, c))
        return
    child.age = int(message.text)
    if child.age >= profile.age:
        bot.send_message(message.chat.id, "Ваш ребенок старше Вас? Введите корректный возраст ребенка в формате числа. Если Вы совершили ошибку в своем возрасте, введите /start и заполните анкету заново")
        bot.register_next_step_handler(message, lambda msg, p=profile, c=child: process_child_age_step(msg, p, c))
        return
    elif child.age >= profile.age - 6:
        bot.send_message(message.chat.id, "Возраст ребенка подозрительно большой. Введите корректный возраст ребенка. Если Вы совершили ошибку, введите /start и заполните анкету заново")
        bot.register_next_step_handler(message, lambda msg, p=profile, c=child: process_child_age_step(msg, p, c))
        return
    bot.send_message(message.chat.id, "Описание ребенка:")
    bot.register_next_step_handler(message, lambda msg, p=profile, c=child: process_child_description_step(msg, p, c))


def process_child_description_step(message, profile, child):
    child.description = message.text
    current_index = len(profile.children) - 1
    if current_index + 1 < profile.num_of_children:
        next_index = current_index + 1
        bot.send_message(message.chat.id, f"Введите информацию о {next_index + 1}-м ребенке:")
        bot.send_message(message.chat.id, "Имя ребенка:")
        bot.register_next_step_handler(message, process_child_info_step, profile)
    else:
        update_profile(message.chat.id, profile)
        bot.send_message(message.chat.id, "Информация о детях сохранена.")
        bot.send_message(message.chat.id, "Ваши профиль успешно создан или обновлен!")
        fill_psycho_test(message, profile.sex)


def fill_psycho_test(message, sex):
    text = """Теперь Вам необходимо будет пройти небольшое психологическое тестирование, которое определит Ваш взгляд на воспитание детей. Отвечайте максимально искренне.

Вам будут предложены варианты ответов от 1 до 5, где:
1 - точно нет
2 - скорее нет, чем да
3 - затрудняюсь ответить
4 - скорее да, чем нет
5 - точно да"""
    bot.send_message(message.chat.id, text)
    tg_id = message.chat.id
    psycho_test = get_psycho_test(tg_id)
    if not psycho_test:
        psycho_test = PsychoTestResult()
        add_psycho_test(tg_id, psycho_test)
    psycho_test.answers.clear()
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('1', '2', '3', '4', '5')
    if sex == Sex['FEMALE']:
        questions = FEMALE_QUESTIONS
    else:
        questions = MALE_QUESTIONS
    bot.send_message(message.chat.id, questions[len(psycho_test.answers)], reply_markup=keyboard)
    bot.register_next_step_handler(message, get_answer,psycho_test, sex)


def get_answer(message, psycho_test, sex):
    if message.text not in ['1', '2', '3', '4', '5']:
        bot.send_message(message.chat.id, '''Пожалуйста, введите корректный вариант ответа:

1 - точно нет
2 - скорее нет, чем да
3 - затрудняюсь ответить
4 - скорее да, чем нет
5 - точно да''')
        bot.register_next_step_handler(message, get_answer, psycho_test, sex)
        return
    psycho_test.answers.append(int(message.text))
    if len(psycho_test.answers) == len(FEMALE_QUESTIONS):
        psycho_test_result_message = get_result_message(psycho_test.answers, sex)
        big_message = f'''Большое спасибо за прохождение психологического тестирования! 

{psycho_test_result_message}

Подбор собеседников отталкивается от схожих взглядах на воспитание детей. Прохождение тестирования сделает подбор более качественным.'''
        bot.send_message(message.chat.id, big_message)
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('только женщин', 'только мужчин', 'и мужчин и женщин')
        bot.send_message(message.chat.id, "Собеседников какого пола Вы бы хотели найти?", reply_markup=keyboard)
        bot.register_next_step_handler(message, sex_filter, psycho_test)
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('1', '2', '3', '4', '5')
        if sex == Sex['FEMALE']:
            questions = FEMALE_QUESTIONS
        else:
            questions = MALE_QUESTIONS
        bot.send_message(message.chat.id, questions[len(psycho_test.answers)], reply_markup=keyboard)
        bot.register_next_step_handler(message, get_answer, psycho_test, sex)


def sex_filter(message, test):
    if message.text not in ['только женщин', 'только мужчин', 'и мужчин и женщин']:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('только женщин', 'только мужчин', 'и мужчин и женщин')
        bot.send_message(message.chat.id, "Ответ некорректен. Выберите пол из предложенных:", reply_markup=keyboard)
        bot.register_next_step_handler(message, sex_filter, test)
        return
    test.answers.append(message.text)
    update_psycho_test(message.chat.id, test)
    bot.send_message(message.chat.id, '''Хорошо. Теперь введите команду /search для того, чтобы начать поиск собеседников. 

Для показа всех доступных команд введите /help''', reply_markup=telebot.types.ReplyKeyboardRemove())


if __name__ == '__main__':
    profiles.create_database()
    psycho_test_results.create_database()
    matching.create_database()
    bot.polling(none_stop=True)