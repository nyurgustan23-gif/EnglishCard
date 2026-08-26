import os

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()
db_name = "EnglishCard"
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")


def create():
    conn = psycopg2.connect(
        database="postgres", user=db_user, password=db_password
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    try:
        cur.execute("CREATE DATABASE EnglishCard;")
        print("Успешно создано")
    except psycopg2.errors.DuplicateDatabase:
        print("БД существует")
    finally:
        cur.close()
        conn.close()


def get_db_connection(database, user, password):
    return psycopg2.connect(database=database, user=user, password=password)


conn = get_db_connection(db_name, db_user, db_password)


def init_database():
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
                username VARCHAR(50) NOT NULL UNIQUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS common_words(
                id BIGSERIAL PRIMARY KEY,
                russian_word VARCHAR NOT NULL,
                english_word VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE (russian_word, english_word)
                );
                """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_words(
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(id),
                russian_word VARCHAR NOT NULL,
                english_word VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE (user_id, russian_word, english_word));
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


def add_user(username):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users(username)
            VALUES (%s)
            ON CONFLICT(username)
            DO UPDATE SET username = EXCLUDED.username
            RETURNING id;
            """,
            (username,),
        )
        id = cur.fetchone()[0]
        conn.commit()
        return id


def add_word(russian_word, english_word):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO common_words(russian_word, english_word)
            VALUES (%s, %s)
            ON CONFLICT (russian_word, english_word)
            DO NOTHING;
        """,
            (
                russian_word,
                english_word,
            ),
        )
        conn.commit()


def user_words(user_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM user_words
            WHERE user_id = %s; 
            """,
            (user_id,),
        )
        user_raw = cur.fetchall()
        cur.execute("""
            SELECT * FROM common_words;
            """)
        common_raw = cur.fetchall()
        words_raw = [user_raw, common_raw]

        return words_raw


def add_user_word(user_id, russian_word, english_word):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO user_words(
                user_id, russian_word, english_word
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (
                user_id, russian_word, english_word
            )
            DO NOTHING;
            """,
            (
                user_id,
                russian_word,
                english_word,
            ),
        )
        conn.commit()
        return cur.rowcount


def delete_user_word(user_id, word_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM user_words WHERE user_id = %s AND id = %s;
            """,
            (
                user_id,
                word_id,
            ),
        )
        conn.commit()
        return cur.rowcount


def update_st(user_id, word_id, word_type, is_correct):
    with conn.cursor() as cur:
        cur.execute(
            """
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
            """,
            (user_id, word_id, word_type, 1 if is_correct else 0),
        )
        conn.commit()


def get_st(user_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT sum(correct_answers), sum(total_attempts) 
            FROM learning_stats
            WHERE user_id = %s;
        """,
            (user_id,),
        )
        data = cur.fetchone()
        return data


create()
