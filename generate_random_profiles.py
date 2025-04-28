import random
import sqlite3

from profiles import Profile, Child, Sex
from profiles import add_profile, remove_profile
from psycho_test_results import PsychoTestResult
from psycho_test_results import add_psycho_test, remove_psycho_test
import profiles
import psycho_test_results
import cities

russian_names = [
    "Александр", "Максим", "Иван", "Дмитрий", "Андрей", "Сергей", "Алексей", "Никита", "Михаил", "Егор",
    "Артём", "Кирилл", "Матвей", "Роман", "Владимир", "Илья", "Олег", "Тимофей", "Павел", "Глеб",
    "Юрий", "Степан", "Леонид", "Борис", "Анатолий", "Виктор", "Василий", "Григорий", "Валерий", "Константин",
    "Тимур", "Руслан", "Аркадий", "Ярослав", "Евгений", "Антон", "Фёдор", "Даниил", "Станислав", "Николай",
    "Виталий", "Геннадий", "Захар", "Игнат", "Пётр", "Мирон", "Альберт", "Арсен", "Вадим", "Денис",
    "Игорь", "Лев", "Святослав", "Прохор", "Тарас", "Тихон", "Ян", "Всеволод", "Георгий", "Елисей",
    "Добрыня", "Гавриил", "Лука", "Сава", "Филипп", "Эдуард", "Эмиль", "Родион", "Марат", "Валентин",
    "Авдей", "Агафон", "Аким", "Александрия", "Арсений", "Вениамин", "Герман", "Давид", "Емельян", "Зиновий",
    "Иосиф", "Клим", "Кузьма", "Лонгин", "Марк", "Наум", "Пантелеймон", "Рубен", "Семён", "Тит",
    "Ульян", "Фадей", "Харитон", "Эльдар", "Юлиан", "Яков", "Артемий", "Виссарион", "Ерофей", "Остап"
]

russian_female_names = [
    "Анна", "Мария", "Екатерина", "Дарья", "Ольга", "Наталья", "Татьяна", "Ирина", "Анастасия", "Юлия",
    "Светлана", "Виктория", "Елена", "Алёна", "Полина", "Вероника", "Ксения", "Марина", "Любовь", "Валентина",
    "Елизавета", "Нина", "Зоя", "Людмила", "Галина", "Алиса", "Оксана", "Инна", "Алина", "Яна",
    "Ева", "Софья", "Варвара", "Милана", "Диана", "Кристина", "Василиса", "Карина", "Аделина", "Лариса",
    "Эльвира", "Тамара", "Регина", "Злата", "Ярослава", "Серафима", "Арина", "Надежда", "Лилия", "Римма",
    "Рената", "Снежана", "Любава", "Ульяна", "Влада", "Агата", "Мира", "Мирослава", "Таисия", "Стефания",
    "Аврора", "Наталия", "Вера", "Жанна", "Эвелина", "Эмма", "Лидия", "Агния", "Анжелика", "Ядвига",
    "Майя", "Маргарита", "Изабелла", "Нелли", "Раиса", "Ася", "Гузель", "Залина", "Сабина", "Фаина",
    "Божена", "Лея", "Олеся", "Валерия", "Клара", "Роза", "София", "Ника", "Айгуль", "Лариса",
    "Юлиана", "Нонна", "Грета", "Жанетта", "Зинаида", "Амелия", "Капитолина", "Элеонора", "Берта", "Пелагея"
]

russian_surnames = [
    "Иванов", "Смирнов", "Кузнецов", "Попов", "Соколов", "Лебедев", "Козлов", "Новиков", "Морозов", "Петров",
    "Волков", "Соловьёв", "Васильев", "Зайцев", "Павлов", "Семёнов", "Голубев", "Виноградов", "Богданов", "Воробьёв",
    "Фёдоров", "Михайлов", "Беляев", "Тарасов", "Белов", "Комаров", "Орлов", "Киселёв", "Макаров", "Андреев",
    "Ковалёв", "Ильин", "Гусев", "Титов", "Кузьмин", "Кудрявцев", "Баранов", "Куликов", "Алексеев", "Степанов",
    "Яковлев", "Сорокин", "Сергеев", "Романов", "Захаров", "Борисов", "Королёв", "Герасимов", "Пономарёв", "Григорьев",
    "Лазарев", "Медведев", "Ершов", "Никитин", "Соболев", "Рябов", "Поляков", "Цветков", "Данилов", "Жуков",
    "Фролов", "Журавлёв", "Николаев", "Крылов", "Максимов", "Сидоров", "Осипов", "Белоусов", "Федотов", "Дорофеев",
    "Егоров", "Матвеев", "Бобров", "Дмитриев", "Калинин", "Анисимов", "Петухов", "Антонов", "Тимофеев", "Никифоров",
    "Веселов", "Филиппов", "Марков", "Большаков", "Суханов", "Миронов", "Ширяев", "Александров", "Коновалов", "Шестаков",
    "Казаков", "Ефимов", "Денисов", "Громов", "Фомин", "Давыдов", "Мельников", "Щербаков", "Блинов", "Колесников"
]

russian_female_surnames = [
    "Иванова", "Смирнова", "Кузнецова", "Попова", "Соколова", "Лебедева", "Козлова", "Новикова", "Морозова", "Петрова",
    "Волкова", "Соловьёва", "Васильева", "Зайцева", "Павлова", "Семёнова", "Голубева", "Виноградова", "Богданова", "Воробьёва",
    "Фёдорова", "Михайлова", "Беляева", "Тарасова", "Белова", "Комарова", "Орлова", "Киселёва", "Макарова", "Андреева",
    "Ковалёва", "Ильина", "Гусева", "Титова", "Кузьмина", "Кудрявцева", "Баранова", "Куликова", "Алексеева", "Степанова",
    "Яковлева", "Сорокина", "Сергеева", "Романова", "Захарова", "Борисова", "Королёва", "Герасимова", "Пономарёва", "Григорьева",
    "Лазарева", "Медведева", "Ершова", "Никитина", "Соболева", "Рябова", "Полякова", "Цветкова", "Данилова", "Жукова",
    "Фролова", "Журавлёва", "Николаева", "Крылова", "Максимова", "Сидорова", "Осипова", "Белоусова", "Федотова", "Дорофеева",
    "Егорова", "Матвеева", "Боброва", "Дмитриева", "Калинина", "Анисимова", "Петухова", "Антонова", "Тимофеева", "Никифорова",
    "Веселова", "Филиппова", "Маркова", "Большакова", "Суханова", "Миронова", "Ширяева", "Александрова", "Коновалова", "Шестакова",
    "Казакова", "Ефимова", "Денисова", "Громова", "Фомина", "Давыдова", "Мельникова", "Щербакова", "Блинова", "Колесникова"
]


def generate_profile():
    profile = Profile()
    sex = random.choice(['m', 'f'])
    profile.name = random.choice(russian_names if sex == 'm' else russian_female_names)
    profile.surname = random.choice(russian_surnames if sex == 'm' else russian_female_surnames)
    profile.sex = Sex.MALE if sex == 'm' else Sex.FEMALE
    profile.age = random.randint(20, 50)
    profile.photo = random.choice(['AgACAgIAAxkBAAIESWgMCDl0jOOU0dLjt88te8JKOhxGAAJl7jEbJahhSEeloJyrhwyOAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIETWgMCD7RLdzcbab8PazruRpYm85VAAJm7jEbJahhSKNAPSBURtnIAQADAgADeAADNgQ', 'AgACAgIAAxkBAAIEUWgMCEQkzMNwermbHev8kBsoUhukAAJn7jEbJahhSFIXkESNatZsAQADAgADeAADNgQ', 'AgACAgIAAxkBAAIEVWgMCEl18qpJnVLNkjbwM4u-JjByAAJo7jEbJahhSPtLt9fShvZUAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEWWgMCE34cnF9T4jVyzxDbwIsnh17AAJp7jEbJahhSA-PBNUKcBBmAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEXWgMCFI-7gsbHfm8TW5YGHIgcDyAAAJq7jEbJahhSGEbwnyJ8C3oAQADAgADeAADNgQ', 'AgACAgIAAxkBAAIEYWgMCFcFjysPziH76ESRtBGKfMy1AAJr7jEbJahhSDPcTBbbg577AQADAgADeAADNgQ', 'AgACAgIAAxkBAAIEZWgMCFtlNfFgvn4bVAsMgHdrednfAAJs7jEbJahhSDjcoN3BrwWjAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEaWgMCGEzUKm_gjd2IrKauM_1uFVyAAJt7jEbJahhSNd5hfW4GwLAAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEbWgMCGj2Yg51VyhtwojVKPHUcLP8AAJu7jEbJahhSCwyPF_uY-QwAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEcWgMCHmxUaTcdFnjqfgC72U05yKwAAJv7jEbJahhSPtes7oDmR-6AQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEdWgMCH6ShkPNGYlLUP28Pa-OSd0pAAJw7jEbJahhSG5jFp234KdKAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEeWgMCILkiZuc-hYTaNM6MLt9xBeOAAJx7jEbJahhSPbdUjsfxzj3AQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEfWgMCIceCczxFaKEmd_CmMXYqPS2AAJy7jEbJahhSOvMxF8gbp1lAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEgWgMCJAWxIHsYMfiT9BD4t6CmOa0AAJz7jEbJahhSBrmJDkIzYeqAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEhWgMCJTi4SM-J9_aykBJ0U2PEturAAJ07jEbJahhSAS3NJ5_Q5K7AQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEiWgMCJmx5SUK6x6sVhNEeaY4Ft0xAAJ17jEbJahhSA9NDtJ8ap9QAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEjWgMCJ_rLOdnVWzdMLzD3pXPG48gAAJ27jEbJahhSCQq8WefFMXqAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEkWgMCKOL7WiLgx2uzkwtJdpv0IzQAAJ37jEbJahhSJOlE-19mDOqAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIElWgMCKfnf8QjlOYYrm9fhMB3HI4HAAJ47jEbJahhSIXnvwNxMGhIAQADAgADeQADNgQ', 'AgACAgIAAxkBAAIEmWgMCLFlho8c8H8rhSBloSy46QIAA3nuMRslqGFIo1zgwBO-cXoBAAMCAAN5AAM2BA'])
    profile.num_of_children = random.randint(0, 3)
    for i in range(profile.num_of_children):
        child = Child()
        children_sex = random.choice(['m', 'f'])
        child.name = random.choice(russian_names if children_sex == 'm' else russian_female_names)
        child.sex = Sex.MALE if children_sex == 'm' else Sex.FEMALE
        child.age = random.randint(1, min(profile.age - 16, 12))
        child.description = random.choice(['умный', "красивый", "спокойный", "нервный", "тихий", "любопытный", "любит трогать траву", "мечтает поступить на фкн", "мечтает, чтобы автор бота закрыла курсач", "умеет складыват числа в уме", "знает, сколько планет в солнечной системе", "прыгает на скакалке 24 часа в сутки", "долбит по батарее металлическим половником", "рисует... на стенах"])
        profile.children.append(child)
    profile.city = random.choice(list(cities.all_cities.keys()))
    profile.district = random.choice(list(cities.all_cities[profile.city]))

    test = PsychoTestResult()
    test.answers = [random.randint(1, 5) for _ in range(10)]
    test.answers.append(random.choice(['только мужчин', "только женщин", "и мужчин и женщин"]))
    return profile, test


def fill_tables():
    for i in range(1000):
        remove_profile(i)
        remove_psycho_test(i)
        profile, answers = generate_profile() # для нуля закомментить это
        print(i) # для нуля
        add_profile(i, profile) # для нуля
        add_psycho_test(i, answers) # для нуля

fill_tables()
