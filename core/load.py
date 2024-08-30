import os
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

def load(data, table_name):

    if not data:  # Early exit if data is empty
        print("No data provided to load.")
        return

    try:
        with mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        ) as connection, connection.cursor() as cursor:
            
            truncate_query = f"TRUNCATE TABLE {table_name};"
            cursor.execute(truncate_query)
            print(f"Table {table_name} truncated successfully.")

            columns = ', '.join(data[0].keys())
            placeholders = ', '.join(['%s'] * len(data[0]))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            data_to_insert = [tuple(item.values()) for item in data]
            
            cursor.executemany(insert_query, data_to_insert)
            connection.commit()
            print(f"All records inserted successfully into {table_name}.")

    except Error as e:
        print(f"Error while inserting into MySQL: {e}")
        if connection.is_connected():
            connection.rollback()

    finally:
        if connection.is_connected():
            print("MySQL connection is closed")