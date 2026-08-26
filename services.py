import random

import database


def login_user(username):
    user_id = database.add_user(username)
    return user_id


def add_common_words():
    words_to_add = [
        ("капуста", "cabbage"),
        ("телевизор", "TV"),
        ("карандаш", "pencil"),
        ("рука", "hand"),
        ("погода", "weather"),
        ("здоровье", "health"),
        ("машина", "car"),
        ("автобус", "bus"),
        ("дверь", "door"),
        ("гора", "mountain"),
    ]
    for rus_w, eng_w in words_to_add:
        database.add_word(rus_w, eng_w)


def get_user_words(user_id):
    words_raw = database.user_words(user_id)
    user_raw = words_raw[0]
    common_raw = words_raw[1]
    all_list = []
    for n in user_raw:
        all_list.append(
            {
                "id": n[0],
                "russian_word": n[2],
                "english_word": n[3],
                "word_type": "user",
            }
        )
    for n in common_raw:
        all_list.append(
            {
                "id": n[0],
                "russian_word": n[1],
                "english_word": n[2],
                "word_type": "common",
            }
        )
    return all_list


def add_personal_word(user_id, russian_word, english_word):
    return database.add_user_word(user_id, russian_word, english_word) == 0


def delete_personal_word(user_id, word_id):
    return database.delete_user_word(user_id, word_id) > 0


def update_stats(user_id, word_id, word_type, is_correct):
    database.update_st(user_id, word_id, word_type, is_correct)


def get_statistics(user_id):
    user_words = get_user_words(user_id)
    data = database.get_st(user_id)
    if data[0] != None:
        n1 = int(data[0])
        n2 = int(data[1])
    else:
        n1 = 0
        n2 = 0
    return {
        "word_count": len(user_words),
        "correct_answers": n1,
        "total_attempts": n2,
    }


def generate_options(user_id):
    word_list = get_user_words(user_id)
    rand_w = random.sample(word_list, 4)
    return rand_w
    