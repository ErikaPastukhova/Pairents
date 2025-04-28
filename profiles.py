import json
import sqlite3
from enum import Enum
import threading


class Sex(Enum):
    NOTHING = 0
    FEMALE = 1
    MALE = 2


class Child:
    def __init__(self) -> None:
        self.name = ''
        self.sex = Sex.NOTHING
        self.age = 0
        self.description = ''


class Profile:
    def __init__(self):
        self.name = ''
        self.surname = ''
        self.sex = Sex.NOTHING
        self.age = -1
        self.photo = None
        self.num_of_children = 0
        self.children = []
        self.city = ''
        self.district = ''


lock = threading.Lock()


def create_database():
    with lock:
        conn = sqlite3.connect('users.db')  # подключаемся к базе данных users.db
        cursor = conn.cursor()
        # сделай в базе данных такую вещь:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                tg_id INTEGER PRIMARY KEY,
                name TEXT,
                surname TEXT,
                sex TEXT,
                age INTEGER,
                photo BLOB,
                num_of_children INTEGER,
                children TEXT,
                city TEXT,
                district TEXT
            )
        ''')
        conn.commit()
        conn.close()


# добавляет id в тг и профиль в таблицу
def add_profile(tg_id, profile):
    with lock:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # умеет записывать пол в таблицу
        def default_serializer(obj):
            if isinstance(obj, Sex):
                return obj.name
            raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

        cursor.execute('''
            INSERT INTO profiles (tg_id, name, surname, sex, age, photo, num_of_children, children, city, district)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tg_id, profile.name, profile.surname, profile.sex.name, profile.age, profile.photo, profile.num_of_children,
              json.dumps([child.__dict__ for child in profile.children], default=default_serializer), profile.city, profile.district))
        conn.commit()
        conn.close()


# из айдишника возвращает класс профиль
def get_profile(tg_id):
    with lock:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM profiles WHERE tg_id = ?', (tg_id,))
        row = cursor.fetchone()
        if row:
            profile = Profile()
            profile.name = row[1]
            profile.surname = row[2]
            profile.sex = Sex[row[3]]
            profile.age = row[4]
            profile.photo = row[5]
            profile.num_of_children = row[6]
            try:
                children_data = json.loads(row[7])
                if isinstance(children_data, list):
                    profile.children = [Child() for _ in range(len(children_data))]
                    for i, child_data in enumerate(children_data):
                        if isinstance(child_data, dict):
                            profile.children[i].name = child_data.get('name', '')
                            profile.children[i].sex = Sex[child_data.get('sex', 'NOTHING')]
                            profile.children[i].age = child_data.get('age', -1)
                            profile.children[i].description = child_data.get('description', '')
            except (ValueError, SyntaxError):
                profile.children = []
            profile.city = row[8]
            profile.district = row[9]
            return profile
        return None


# почти то же самое, что и add_profile, только в скл вместо инсерта андейт
def update_profile(tg_id, profile):
    with lock:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        def default_serializer(obj):
            if isinstance(obj, Sex):
                return obj.name
            raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

        cursor.execute('''
            UPDATE profiles SET name = ?, surname = ?, sex = ?, age = ?, photo = ?, num_of_children = ?, children = ?, city = ?, district = ?
            WHERE tg_id = ?
        ''', (profile.name, profile.surname, profile.sex.name, profile.age, profile.photo, profile.num_of_children,
              json.dumps([child.__dict__ for child in profile.children], default=default_serializer), profile.city, profile.district, tg_id))
        conn.commit()
        conn.close()


# просто удаляет профиль из таблицы
def remove_profile(tg_id):
    with lock:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM profiles WHERE tg_id = ?', (tg_id,))
        conn.commit()
        conn.close()


def get_all_ids():
    with lock:
        conn = sqlite3.connect("users.db")
        rows = conn.execute("SELECT tg_id FROM profiles").fetchall()
        conn.close()
    return [r[0] for r in rows]


def str_from_age(age):
    str_age = ''
    if 11 <= age % 100 <= 14:
        str_age = 'лет'
    else:
        last_digit = age % 10
        if last_digit == 1:
            str_age = 'год'
        elif 2 <= last_digit <= 4:
            str_age = 'года'
        else:
            str_age = 'лет'
    return str_age


def profile_as_text(profile):
    response = f"""{profile.name} {profile.surname} ({'М' if profile.sex.name == 'MALE' else 'Ж'}), {profile.age} {str_from_age(profile.age)}
{profile.city}, {profile.district}
Количество детей: {profile.num_of_children}\n"""

    for i, child in enumerate(profile.children):
        response += f"""\nИнформация о {i + 1}-м ребенке:
{child.name} ({'М' if child.sex.name == 'MALE' else 'Ж'}), {child.age} {str_from_age(child.age)}
Описание: {child.description}\n"""

    return response, profile.photo