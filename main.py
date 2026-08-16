"""
EnglishCard - Приложение для изучения английского языка
Базовый файл-заготовка для курсовой работы
Студенту необходимо доработать этот файл в соответствии с заданием
"""

import streamlit as st
import psycopg2 
import pandas as pd
import random

# ============================================================
# НАСТРОЙКА СТРАНИЦЫ
# ============================================================
st.set_page_config(
    page_title="EnglishCard - Изучение английского",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# РАБОТА С БАЗОЙ ДАННЫХ
# ============================================================

def get_db_connection():
    return psycopg2.connect(
        database='', 
        user='', 
        password=''
    )


def init_database():
    conn = get_db_connection()
    with conn.cursor() as cur:
        # cur.execute("""
        #     DROP TABLE IF EXISTS learning_stats;
        #     DROP TABLE IF EXISTS user_words;
        #     DROP TABLE IF EXISTS common_words;
        #     DROP TABLE IF EXISTS users;
        # """
        # )
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id BIGSERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
        """
        )
        cur.execute("""
            CREATE TABLE IF NOT EXISTS common_words(
                id BIGSERIAL PRIMARY KEY,
                russian_word VARCHAR NOT NULL,
                english_word VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
                );
                """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_words(
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(id),
                russian_word VARCHAR NOT NULL,
                english_word VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
                );
                """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS learning_stats(
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(id),
                word_id BIGINT NOT NULL,
                word_type VARCHAR(50) NOT NULL,
                correct_answers BIGINT,
                total_attempts BIGINT ,
                last_reviewed TIMESTAMP,
                UNIQUE (user_id, word_id, word_type)
                );
                """)
        conn.commit()


def login_user(username):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM users WHERE username=%s;
            """, (username,))
            id = cur.fetchone()
            if id == None:
                cur.execute("""
                    INSERT INTO users(username)
                    VALUES (%s)
                    RETURNING id;
                    """, (username,))
                new_user = cur.fetchone()
                return new_user[0]
            else:
                return id[0]


def add_word(russian_word, english_word):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM common_words
                WHERE russian_word = %s AND english_word = %s;
            """, (russian_word, english_word,))
            id = cur.fetchone()
            if id == None:
                cur.execute("""
                    INSERT INTO common_words(russian_word, english_word)
                    VALUES (%s, %s);
                """, (russian_word, english_word,))


def add_common_words():
    add_word('капуста', 'cabbage')
    add_word('телевизор', 'TV')
    add_word('карандаш', 'pencil')
    add_word('рука', 'hand')
    add_word('погода', 'weather')
    add_word('здоровье', 'health')
    add_word('машина', 'car')
    add_word('автобус', 'bus')
    add_word('дверь', 'door')
    add_word('гора', 'mountain')


def get_user_words(user_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM user_words
                WHERE user_id = %s; 
                """, (user_id,))
            user_all = cur.fetchall()
            cur.execute("""
                SELECT * FROM common_words;
                """)
            common_all = cur.fetchall()
            all_list = []
            if user_all != None:
                for n in user_all:
                    all_list.append(
                            {
                            'id': n[0], 
                            'russian_word': n[2], 
                            'english_word': n[3], 
                            'word_type': 'user',
                            }
                        )
            for n in common_all:
                all_list.append(
                    {
                    'id': n[0], 
                    'russian_word': n[1], 
                    'english_word': n[2], 
                    'word_type': 'common',
                    }
                )
            return all_list


def add_personal_word(user_id, russian_word, english_word):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM user_words 
                WHERE user_id = %s AND russian_word = %s AND english_word = %s;
                """, (user_id, russian_word, english_word))
            u_word = cur.fetchone()
            if u_word != None:
                return True
            else:
                cur.execute("""
                    INSERT INTO user_words(user_id, russian_word, english_word)
                    VALUES (%s, %s, %s);
                    """, (user_id, russian_word, english_word,))
                return False


def delete_personal_word(user_id, word_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT FROM user_words WHERE user_id = %s AND id = %s;
                """, (user_id, word_id,))
            word = cur.fetchone()
            if word != None:
                cur.execute("""
                    DELETE FROM user_words WHERE user_id = %s AND id = %s;
                    """, (user_id, word_id,))
                return True
            else:
                return False
            

def update_stats(user_id, word_id, word_type, is_correct):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO learning_stats(
                    user_id,
                    word_id, 
                    word_type, 
                    correct_answers, 
                    total_attempts, 
                    last_reviewed
                )
                VALUES (%s, %s, %s, %s, 1, NOW())
                ON CONFLICT (user_id, word_id, word_type)
                DO UPDATE SET
                    correct_answers = learning_stats.correct_answers + 
                        EXCLUDED.correct_answers,
                    total_attempts = learning_stats.total_attempts + 1,
                    last_reviewed = NOW();
                """, (user_id, word_id, word_type, 1 if is_correct else 0))


def get_statistics(user_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT sum(correct_answers), sum(total_attempts) FROM learning_stats
                WHERE user_id = %s;
            """, (user_id,))
            data = cur.fetchone()
            if data[0] != None:
                return {
                    'word_count': len(get_user_words(user_id)), 
                    'correct_answers': int(data[0]), 
                    'total_attempts': int(data[1]),
                }
            else:
                return {
                    'word_count': len(get_user_words(user_id)), 
                    'correct_answers': '0', 
                    'total_attempts': '0',
                }


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def generate_options():
    if 'rand_w' not in st.session_state:
        rand_w = []
        while len(rand_w) <= 3:
            a = random.choice(get_user_words(st.session_state.user_id))
            if a not in rand_w:
                rand_w.append(a)
        st.session_state.rand_w = rand_w
    if 'current_word' not in st.session_state:
        st.session_state.current_word = random.choice(st.session_state.rand_w)


def check_word(word):
    if word == st.session_state.current_word:
        update_stats(
            st.session_state.user_id, 
            st.session_state.current_word['id'], 
            st.session_state.current_word['word_type'], 
            True
        )
        st.session_state.answer = True
    else:
        update_stats(
            st.session_state.user_id, 
            st.session_state.current_word['id'], 
            st.session_state.current_word['word_type'], 
            False
        )
        st.session_state.answer = False


def new_random():
    rand_w = []
    while len(rand_w) <= 3:
        a = random.choice(get_user_words(st.session_state.user_id))
        if a not in rand_w:
            rand_w.append(a)
    st.session_state.rand_w = rand_w
    st.session_state.current_word = random.choice(st.session_state.rand_w)


def reset_answer():
    st.session_state.answer = None


def next_word():
    new_random()
    reset_answer()


# ============================================================
# ИНТЕРФЕЙС ПРИЛОЖЕНИЯ
# ============================================================

def render_sidebar():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    with st.sidebar:
        if not st.session_state.logged_in:
            st.title('Авторизация')
            username = st.text_input('Введите логин: ')
            if st.button('Войти / Зарегистрироваться'):
                st.success(f'Добро пожаловать, {username}!', icon="✅")
                user_id = login_user(username)
                st.session_state.logged_in = True
                st.session_state.answer = None
                if 'username' not in st.session_state:
                    st.session_state.username = username
                    st.session_state.user_id = user_id
                    print(user_id)
                else:
                    if st.session_state.username != username:
                        st.session_state.username = username
                        st.session_state.user_id = user_id
                        print(user_id)
                st.rerun()
        else:
            st.title('👤Профиль')
            st.success(f'Вы вошли как: {st.session_state.username}')
            if st.button('Выйти'):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.rerun()


def render_study_tab():
    generate_options()
    if 'answer' not in st.session_state:
        st.session_state.answer = None
    st.header('📖Изучаем слова')
    st.subheader(f'Слово: {st.session_state.current_word['russian_word']}')
    st.subheader('Как будет по-английски?')
    st.subheader('Выберите перевод:')

    but1, but2, but3, but4 = st.columns(4)

    with but1:
        if st.button(
            st.session_state.rand_w[0]['english_word'], 
            use_container_width=True, key='1'
        ):
            check_word(st.session_state.rand_w[0])
    with but2:
        if st.button(
            st.session_state.rand_w[1]['english_word'], 
            use_container_width=True, key='2'
        ):
            check_word(st.session_state.rand_w[1])
    with but3:
        if st.button(
            st.session_state.rand_w[2]['english_word'], 
            use_container_width=True, key='3'
        ):
            check_word(st.session_state.rand_w[2])
    with but4:
        if st.button(
            st.session_state.rand_w[3]['english_word'], 
            use_container_width=True, key='4'
        ):
            check_word(st.session_state.rand_w[3])
            
    st.button('➡️Следующее слово', on_click=next_word, use_container_width=True)
        
    if st.session_state.answer != None:
        if st.session_state.answer == True:
            st.success('✅Правильно!')
        else:
            st.text('Попробуйте ещё')


def render_add_word_tab():
    rus_w = st.text_input('Введите русское слово: ')
    eng_w = st.text_input('Введите перевод: ')
    if st.button('Добавить слово'):
        if add_personal_word(st.session_state.user_id, rus_w, eng_w) == True:
            st.error('Такое слово уже существует.')
        else:
            st.success('Слово добавлено.')


def render_delete_word_tab():
    user_words_raw = get_user_words(st.session_state.user_id)
    user_words = []
    for n in user_words_raw:
        if n['word_type'] == 'user':
            user_words.append(n)
    word = st.selectbox('Выберите слово:', user_words)
    if word != None:
        st.button(
            'Удалить слово', 
            on_click=delete_personal_word, 
            args=[st.session_state.user_id, word['id']]
        )


def render_statistics_tab(user_id):
    st.header(f'{get_statistics(st.session_state.user_id)}')


    # """
    # TODO: Реализовать вкладку статистики (дополнительное требование)
    # - Количество изученных слов
    # - Количество попыток
    # - Процент правильных ответов
    # - История последних попыток
    # """
    # pass


def render_schema():
    """
    TODO: Реализовать отображение схемы базы данных (дополнительное требование)
    """
    pass


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """
    Главная функция приложения
    TODO: Реализовать основную логику:
    1. Инициализация БД
    2. Авторизация пользователя
    3. Отображение вкладок с функционалом
    4. Приветственное сообщение для неавторизованных пользователей
    """
    
    st.title("📚 EnglishCard - Изучай английский с удовольствием!")
    
    # TODO: Инициализация состояния сессии
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    init_database()

    add_common_words()
    
    render_sidebar()
    
    if st.session_state.user_id:
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📖 Изучение", 
                "➕ Добавить слово", 
                "🗑️ Удалить слово", 
                "📊 Статистика"
            ]
        )
        with tab1:
            render_study_tab()
        with tab2:
            render_add_word_tab()
        with tab3:
            render_delete_word_tab()
        with tab4:
            pass
    else:
        st.header('Привет, это приложение для изучения английского - EnglishCard!')
        st.subheader('Войдите чтобы начать.')

if __name__ == "__main__":
    main()