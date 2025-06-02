import psycopg

def get_connection():
    return psycopg.connect(
        dbname="alp",
        user="izzet",
        password="",
        host="localhost",
        port="5432"
    )
