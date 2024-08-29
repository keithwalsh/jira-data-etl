import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables from the .env file located in the parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

def load(data, table_name):
    try:
        # Establish MySQL connection
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
        cursor = connection.cursor()

        # Generate column and placeholder strings from data keys
        columns = list(data[0].keys()) if data else []
        columns_list = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        
        # Formulate the TRUNCATE and INSERT queries
        truncate_query = f"TRUNCATE TABLE {table_name};"
        insert_query = f"""
        INSERT INTO {table_name} (
            {columns_list}
        ) VALUES ({placeholders})
        """
        
        # Truncate the table before inserting new data
        cursor.execute(truncate_query)
        print(f"Table {table_name} truncated successfully.")

        # Insert data into the table
        cursor.executemany(insert_query, [tuple(value[col] for col in columns) for value in data])
        connection.commit()
        print("All records inserted successfully.")

    except Error as e:
        print("Error while inserting into MySQL", e)
        connection.rollback()  # Rollback in case of error
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")