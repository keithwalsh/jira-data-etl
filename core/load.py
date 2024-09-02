import os
import mysql.connector
from mysql.connector import Error

def load(data: list, table_name: str):
    if not data:
        return print("No data provided to load.")
    try:
        connection = mysql.connector.connect(**{param: os.getenv(f"MYSQL_{param.upper()}") for param in ["host", "port", "user", "password", "database"]})
        with connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE {table_name};")
            insert_query = f"INSERT INTO {table_name} ({', '.join(data[0].keys())}) VALUES ({', '.join(['%s'] * len(data[0]))})"
            cursor.executemany(insert_query, [tuple(item.values()) for item in data])
            connection.commit()
            print(f"All records inserted successfully into {table_name}.")
    except Error as e:
        print(f"Database Error: {e}")
    finally:
        if connection.is_connected():
            connection.close()  