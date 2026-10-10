import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="H@bIb93633",
        database="sorim_itsm"
    )