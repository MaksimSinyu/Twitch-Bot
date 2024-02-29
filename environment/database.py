from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from environment.config import DATABASE_URL
import mysql.connector

from src.utils import socials_to_string, socials_to_list

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="testdb",
)

cursor = db.cursor()
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(engine)


def delete_database(name):
    cursor.execute(f'DROP DATABASE IF EXISTS {name}')


def create_local_database():
    cursor.execute('CREATE DATABASE IF NOT EXISTS testdb')
    cursor.execute('USE testdb')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel (
            id int PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50),
            dota_player_id int UNSIGNED,
            donation_link VARCHAR(100),
            socials VARCHAR(200),
            language_choice VARCHAR(10)
        );''')
    cursor.execute('DESCRIBE channel')






