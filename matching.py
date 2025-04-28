import json
import sqlite3
import threading
import psycho_test_results
import profiles
import cities
from collections import Counter


def is_match(user1, user2):
    profile1 = profiles.get_profile(user1)
    answers1 = psycho_test_results.get_psycho_test(user1).answers
    popular_psycho_test_answer1 = Counter(answers1[:10]).most_common(1)[0][0]
    search_sex1 = None
    if answers1[10] == 'только мужчин':
        search_sex1 = profiles.Sex['MALE']
    elif answers1[10] == 'только женщин':
        search_sex1 = profiles.Sex['FEMALE']

    profile2 = profiles.get_profile(user2)
    answers2 = psycho_test_results.get_psycho_test(user2).answers
    popular_psycho_test_answer2 = Counter(answers2[:10]).most_common(1)[0][0]
    search_sex2 = None
    if answers2[10] == 'только мужчин':
        search_sex2 = profiles.Sex['MALE']
    elif answers2[10] == 'только женщин':
        search_sex2 = profiles.Sex['FEMALE']

    if (search_sex1 is not None and search_sex1 != profile2.sex) or (search_sex2 is not None and search_sex2 != profile1.sex):
        return False

    if popular_psycho_test_answer1 != popular_psycho_test_answer2:
        return False

    common_districts = set(cities.all_cities[profile1.city][profile1.district]) & set(cities.all_cities[profile2.city][profile2.district])
    if not common_districts:
        return False

    return True


lock = threading.Lock()

def create_database():
    with lock:
        conn = sqlite3.connect('interactions.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                user_id INTEGER,
                target_id INTEGER,
                status TEXT CHECK(status IN ('i want to marry him', 'hmm', 'fe')),
                skip_index INTEGER,
                PRIMARY KEY (user_id, target_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_state (
                user_id INTEGER PRIMARY KEY,
                view_index INTEGER DEFAULT 0
            )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user_target ON interactions(user_id, target_id);")
        conn.commit()
        conn.close()


def like_candidate(user_id, target_id, bot):
    with lock:
        conn = sqlite3.connect("interactions.db")
        conn.execute("REPLACE INTO interactions (user_id, target_id, status, skip_index) VALUES (?, ?, 'i want to marry him', 0)",
                     (user_id, target_id))
        conn.execute("UPDATE user_state SET view_index = view_index + 1 WHERE user_id = ?",
                     (user_id,))
        conn.commit()
        conn.close()

    with lock:
        conn = sqlite3.connect("interactions.db")
        mutual_like = conn.execute("""
            SELECT 1 FROM interactions 
            WHERE user_id = ? AND target_id = ? AND status = 'i want to marry him'
        """, (target_id, user_id)).fetchone()
        conn.close()

 # ВЫ СМЭЧИЛИСЬ НА СТОКА

# ПОЛЬЗОВАТЕЛЬ САМ ЗАДАЕТ МИНИМАЛЬНЫЙ ПОРОГ НА МЭЧ

    if mutual_like:
        # Отправляем контакты обоим
        for uid, tid in [(user_id, target_id), (target_id, user_id)]:
            target_profile = profiles.get_profile(tid)
            if target_profile is not None:
                target_tg_user = bot.get_chat_member(tid, tid)
                bot.send_message(uid, f'''Поздравляем! У вас взаимная симпатия с пользователем {target_profile.name}!

Свяжитесь с @{target_tg_user.user.username}, чтобы начать общение!''')
                response, photo = profiles.profile_as_text(target_profile)

                if photo:
                    bot.send_photo(user_id, photo, caption=response)
                else:
                    response += "Фотография не загружена."
                    bot.send_message(user_id, response)


def reject_candidate(user_id, target_id):
    with lock:
        conn = sqlite3.connect("interactions.db")
        conn.execute("REPLACE INTO interactions (user_id, target_id, status, skip_index) VALUES (?, ?, 'fe', 0)",
                     (user_id, target_id))
        conn.execute("UPDATE user_state SET view_index = view_index + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()


def skip_candidate(user_id, target_id):
    with lock:
        conn = sqlite3.connect("interactions.db")
        row = conn.execute("SELECT view_index FROM user_state WHERE user_id = ?", (user_id,)).fetchone()
        view_index = row[0] if row else 0
        conn.execute("REPLACE INTO interactions (user_id, target_id, status, skip_index) VALUES (?, ?, 'hmm', ?)",
                     (user_id, target_id, view_index))
        conn.execute("UPDATE user_state SET view_index = view_index + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()


def get_next_candidate(user_id):
    with lock:
        conn = sqlite3.connect("interactions.db")
        view_index_row = conn.execute("SELECT view_index FROM user_state WHERE user_id = ?", (user_id,)).fetchone()
        view_index = view_index_row[0] if view_index_row else 0
        conn.execute("INSERT OR IGNORE INTO user_state (user_id, view_index) VALUES (?, ?)", (user_id, view_index))
        conn.commit()
        conn.close()

    candidates = set(profiles.get_all_ids())

    skips = set()
    rejects = {user_id}

    with lock:
        conn = sqlite3.connect("interactions.db")
        for row in conn.execute("SELECT target_id, status, skip_index FROM interactions WHERE user_id = ?",
                                (user_id,)):
            tid, status, sindex = row # эс индекс это какого по счету чувака юзер пока не послал но и не лайкнул (хмм)
            if status == 'fe' or status == 'i want to marry him':
                rejects.add(tid) # униженные и оскорбленные
            elif status == 'hmm':
                if sindex + 10 > view_index:
                    skips.add(tid)
        conn.close()

    candidates = candidates - rejects

    for candidate_id in (candidates - skips):
        if is_match(user_id, candidate_id):
            return candidate_id

    for candidate_id in (candidates & skips):
        if is_match(user_id, candidate_id):
            return candidate_id

    return None