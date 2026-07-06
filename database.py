import sqlite3

def init_db():
    conn = sqlite3.connect('lessons.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            language TEXT,
            region TEXT,
            title TEXT,
            story TEXT,
            quiz_question TEXT,
            options TEXT,
            correct_answer TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_lesson(topic, language, region, title, story, quiz_question, options, correct_answer):
    conn = sqlite3.connect('lessons.db')
    cursor = conn.cursor()
    options_string = ",".join(options)
    cursor.execute('''
        INSERT INTO lessons (topic, language, region, title, story, quiz_question, options, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (topic, language, region, title, story, quiz_question, options_string, correct_answer))
    conn.commit()
    conn.close()

def get_all_offline_lessons():
    conn = sqlite3.connect('lessons.db')
    cursor = conn.cursor()
    cursor.execute('SELECT topic, language, region, title, story, quiz_question, options, correct_answer FROM lessons')
    rows = cursor.fetchall()
    conn.close()
    return rows