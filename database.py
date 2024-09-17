import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import json

load_dotenv()

def get_db_connection():
    """Fungsi untuk membuat koneksi ke database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_DATABASE'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return None

def save_to_database(audio_file_path, original_text, transcription, differences, accuracy, error_rate):
    """Menyimpan data transkripsi ke database."""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO transcriptions (audio_path, original_text, transcription, differences, accuracy, error_rate)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (audio_file_path, original_text, transcription, json.dumps(differences), accuracy, error_rate))
            connection.commit()
            print("Data berhasil disimpan ke database")
        except Error as e:
            print(f"Error inserting data into MariaDB: {e}")
        finally:
            cursor.close()
            connection.close()
            print("MariaDB connection is closed")
    else:
        print("Koneksi ke database gagal.")

def get_transcription_data(transcription_id):
    """Mengambil data transkripsi berdasarkan ID."""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT audio_path, original_text, transcription, differences, accuracy, error_rate 
            FROM transcriptions 
            WHERE id = %s
            """
            cursor.execute(query, (transcription_id,))
            result = cursor.fetchone()
            if result:
                return result
            else:
                print("Data transkripsi tidak ditemukan.")
                return None
        except Error as e:
            print(f"Error retrieving data from MariaDB: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
            print("MariaDB connection is closed")
    else:
        print("Koneksi ke database gagal.")
        return None
