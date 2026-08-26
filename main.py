import streamlit as st

import database
import services
import ui

def main():
    st.set_page_config(
    page_title="EnglishCard - Изучение английского",
    page_icon="📚",
    layout="wide",
)
    if 'database' not in st.session_state:
        database.create()
        st.session_state.database = True
    database.init_database()
    services.add_common_words()
    st.title("📚 EnglishCard - Изучай английский с удовольствием!")
    ui.render_sidebar()
    if st.session_state.get("logged_in", False):
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📖 Изучение",
                "➕ Добавить слово",
                "🗑️ Удалить слово",
                "📊 Статистика",
            ]
        )
        with tab1:
            ui.render_study_tab()
        with tab2:
            ui.render_add_word_tab()
        with tab3:
            ui.render_delete_word_tab()
        with tab4:
            pass
    else:
        st.header(
            "Привет, это приложение для изучения английского - EnglishCard!"
        )
        st.subheader("Войдите чтобы начать.")

if __name__ == "__main__":
    main()
    