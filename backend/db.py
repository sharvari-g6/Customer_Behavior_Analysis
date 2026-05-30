import psycopg2

def get_connection():
    conn = psycopg2.connect(
        dbname="customer_behavior",
        user="postgres",
        password="namrata@123",
        host="localhost",
        port="5432"
    )
    return conn