import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

def load(data, table_name):
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
        cursor = connection.cursor()

        columns = list(data[0].keys()) if data else []
        columns_list = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        
        truncate_query = f"TRUNCATE TABLE {table_name};"
        insert_query = f"""
        INSERT INTO {table_name} (
            {columns_list}
        ) VALUES ({placeholders})
        """

        cursor.execute(truncate_query)
        print(f"Table {table_name} truncated successfully.")

        cursor.executemany(insert_query, [tuple(value[col] for col in columns) for value in data])
        connection.commit()
        print("All records inserted successfully.")

    except Error as e:
        print("Error while inserting into MySQL", e)
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")