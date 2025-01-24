import sqlite3
import pandas as pd
import csv

db = sqlite3.connect('./features/database/english_tutor.db')
cur = db.cursor()

csv_file = "./engtutor_tasks.csv"
df = pd.read_csv(csv_file)

# cur.execute('''
#     CREATE TABLE IF NOT EXISTS tasks (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         type TEXT,
#         description TEXT,
#         description_url TEXT,
#         answer TEXT,
#         explanation TEXT,
#         explanation_url TEXT
#     )
# ''')


csv_file = "engtutor_tasks.csv"
with open(csv_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)  # Читаем CSV как словарь
    for row in reader:
        # Вставляем данные в таблицу
        cur.execute('''
            INSERT INTO tasks (type, description, description_url, answer, explanation, explanation_url) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (row["type"], row["desc"], row["desc_url"], row["ans"], row["dec"], row["dec_url"]))

# df = pd.read_csv(csv_file)

# # Импортируем данные из CSV
# for _, row in df.iterrows():
#     cur.execute('INSERT INTO tasks (type, description, description_url, answer, explanation, explanation_url) VALUES (?, ?, ?, ?, ?, ?)',
#                 (row["type"], row["desc"], row["desc_url"], row["ans"], row["dec"], row["dec_url"]))

db.commit()
db.close()


