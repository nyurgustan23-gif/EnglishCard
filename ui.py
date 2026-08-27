import random

import streamlit as st

import services


def log_in(username):
    if not username.strip():
        return False
    else:
        user_id = services.login_user(username)
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.user_id = user_id
        st.session_state.welcome = True
        return True


def log_out():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.is_right = None
    st.session_state.current_words = None
    st.rerun()


def render_sidebar():
    if not st.session_state.get("logged_in", False):
        with st.sidebar:
            st.title("Aвторизация")
            username = st.text_input("Введите логин: ")
            if st.button("Войти / Зарегистрироваться"):
                if log_in(username):
                    st.rerun()
                else:
                    st.error("Введите имя пользователя")
    else:
        with st.sidebar:
            st.title("👤Профиль")
            st.success(f"Вы вошли как: {st.session_state.username}")
            if st.button("Выйти"):
                log_out()
            if st.session_state.welcome:
                st.toast(
                    f"Добро пожаловать, {st.session_state.username}!",
                    icon="✅",
                )
                st.session_state.welcome = False


def current_words_init():
    if (
        "current_words" not in st.session_state
        or st.session_state.current_words == None
    ):
        st.session_state.current_words = services.generate_options(
            st.session_state.user_id
        )
        st.session_state.current_word = random.choice(
            st.session_state.current_words
        )
    if "is_right" not in st.session_state:
        st.session_state.is_right = None


def new_words_init():
    if st.session_state.is_right:
        st.session_state.current_words = services.generate_options(
            st.session_state.user_id
        )
        st.session_state.current_word = random.choice(
            st.session_state.current_words
        )
        st.session_state.is_right = None


def check_word(word):
    if word == st.session_state.current_word:
        services.update_stats(
            st.session_state.user_id,
            st.session_state.current_word["id"],
            st.session_state.current_word["word_type"],
            True,
        )
        st.session_state.is_right = True
    else:
        services.update_stats(
            st.session_state.user_id,
            st.session_state.current_word["id"],
            st.session_state.current_word["word_type"],
            False,
        )
        st.session_state.is_right = False


def render_study_tab():
    current_words_init()
    st.header("📖Изучаем слова")
    st.subheader(f"Слово: {st.session_state.current_word['russian_word']}")
    st.subheader("Как будет по-английски?")
    st.subheader("Выберите перевод:")

    but1, but2, but3, but4 = st.columns(4)

    with but1:
        if st.button(
            st.session_state.current_words[0]["english_word"],
            use_container_width=True,
            key="1",
        ):
            if not st.session_state.is_right:
                check_word(st.session_state.current_words[0])
            print(services.get_statistics(st.session_state.user_id))
    with but2:
        if st.button(
            st.session_state.current_words[1]["english_word"],
            use_container_width=True,
            key="2",
        ):
            if not st.session_state.is_right:
                check_word(st.session_state.current_words[1])
            print(services.get_statistics(st.session_state.user_id))
    with but3:
        if st.button(
            st.session_state.current_words[2]["english_word"],
            use_container_width=True,
            key="3",
        ):
            if not st.session_state.is_right:
                check_word(st.session_state.current_words[2])
            print(services.get_statistics(st.session_state.user_id))
    with but4:
        if st.button(
            st.session_state.current_words[3]["english_word"],
            use_container_width=True,
            key="4",
        ):
            if not st.session_state.is_right:
                check_word(st.session_state.current_words[3])
            print(services.get_statistics(st.session_state.user_id))

    if st.session_state.is_right:
        st.button(
            "➡️Следующее слово",
            on_click=new_words_init,
            use_container_width=True,
        )
        st.success("✅Правильно!")
    if st.session_state.is_right == False:
        st.text("Попробуйте ещё раз")


def render_add_word_tab():
    rus_w = st.text_input("Введите русское слово: ")
    eng_w = st.text_input("Введите перевод: ")
    if st.button("Добавить слово"):
        if (
            services.add_personal_word(st.session_state.user_id, rus_w, eng_w)
            == True
        ):
            st.error("Такое слово уже существует.")
        else:
            st.success("Слово добавлено.")


def user_words_list():
    user_words_raw = services.get_user_words(st.session_state.user_id)
    user_words = []
    for n in user_words_raw:
        if n["word_type"] == "user":
            user_words.append(n)
    return user_words


def render_delete_word_tab():
    user_words = user_words_list()
    word = st.selectbox("Выберите слово:", user_words)
    if word != None:
        st.button(
            "Удалить слово",
            on_click=services.delete_personal_word,
            args=[st.session_state.user_id, word["id"]],
        )
