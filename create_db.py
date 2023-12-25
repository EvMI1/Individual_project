import sqlite3

# Создание БД
conn = sqlite3.connect("universities.db")
cursor = conn.cursor()

# Создание таблицы Universities
cursor.execute(
    """CREATE TABLE Universities
                  (id INTEGER PRIMARY KEY,
                   name TEXT,
                   specialties TEXT,
                   min_score REAL,
                   avg_score REAL,
                   duration TEXT,
                   address TEXT,
                   contact TEXT,
                   dormitory TEXT,
                   website TEXT)"""
)

# Заполнение таблицы
data = [
    (
        "1",
        "Московский государственный технический университет имени Н.Э. Баумана",
        "прикладная математика, радиотехника",
        95.0,
        98.2,
        "5 лет",
        "105005 г. Москва, ул. Бауманская, д. 5",
        "+7 (499) 263-65-13",
        "да",
        "www.bmstu.ru",
    ),
    (
        "2",
        "Санкт-Петербургский государственный университет информационных технологий, механики и оптики",
        "программирование, информационная безопасность",
        80.0,
        87.5,
        "4 года",
        "",
        "+7 (812) 316-10-00",
        "да",
        "www.itmo.ru",
    ),
    (
        "3",
        "Новосибирский государственный университет",
        "фундаментальная информатика и компьютерные науки",
        85.0,
        92.0,
        "4 года",
        "630090 г. Новосибирск, ул. Пирогова, д. 2",
        "+7 (383) 330-18-69",
        "да",
        "www.nsu.ru",
    ),
]

cursor.executemany(
    "INSERT INTO Universities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data
)

conn.commit()
conn.close()
