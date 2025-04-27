import logging
import os
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg.sql import SQL
from typing import Any, Dict, List, Optional


class PostgresClient:
    _instance = None  # Хранит единственный экземпляр класса

    def __new__(cls):
        """ Реализация паттерна Singleton """
        if cls._instance is None:
            cls._instance = super(PostgresClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return  # Предотвращаем повторную инициализацию
        self._initialized = True

        """ Загружаем переменные окружения """
        load_dotenv()
        self.dsn = self._build_dsn()
        self.connection = None

    @staticmethod
    def _build_dsn() -> str:
        """ Формирует строку подключения (DSN) на основе переменных окружения """
        try:
            return f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@" \
                   f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        except Exception as e:
            logging.error(f"Failed to build DSN: {e}")
            raise

    def connect(self):
        """ Создает подключение к базе данных """
        try:
            self.connection = psycopg.connect(self.dsn)
            self._init_tables()
            logging.info("Database connection successfully established.")
        except Exception as e:
            logging.error(f"Failed to connect to database: {e}")
            self.connection = None  # Убедитесь, что connection остается None в случае ошибки
            raise

    def close(self):
        """ Закрывает подключение к базе данных """
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")

    def _init_tables(self) -> None:
        """ Создает таблицу images в базе данных, если её еще нет """
        create_table_query = """
                    CREATE TABLE IF NOT EXISTS images (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL,
                        original_name VARCHAR(255) NOT NULL,
                        size INTEGER,
                        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_type VARCHAR(10)
                    )
                """
        try:
            with self.connection.cursor() as cur:
                cur.execute(create_table_query)
                self.connection.commit()
                logging.info("Table 'images' ensured to exist.")
        except Exception as e:
            logging.error(f"Failed to ensure table exists: {e}")
            raise

    def add_image(self, original_name: str, filename: str, size: int, extension: str) -> None:
        """ Добавляет запись о новом изображении в таблицу images """
        query = SQL("INSERT INTO images (filename, original_name, size, file_type) VALUES (%s, %s, %s, %s)")
        self.execute(query, (filename, original_name, size, extension))

    def get_images(self, page: int = 1, limit: int = 1) -> List[Dict[str, Any]]:
        """ Получает список изображений с пагинацией """
        offset = (page - 1) * limit if limit > 1 and page > 1 else 0
        query = SQL("SELECT * FROM images ORDER BY upload_time DESC LIMIT %s OFFSET %s")
        return self.fetchall(query, (limit, offset))

    def get_image_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """ Получает изображение по его ID """
        query = SQL("SELECT id FROM images WHERE filename = %s")
        return self.fetchone(query, (filename,))

    def get_total_images(self) -> int:
        """ Получает общее количество изображений в таблице images """
        query = SQL("SELECT COUNT(*) AS total FROM images")
        result = self.fetchone(query)
        return result['total'] if result else 0

    def delete_image(self, image_id: str) -> None:
        """ Удаляет запись об изображении из таблицы images по ID """
        query = SQL("DELETE FROM images WHERE id = %s")
        self.execute(query, (image_id,))

    def execute(self, query: SQL, params: Optional[tuple] = None) -> None:
        """ Выполняет SQL-запрос без возврата результатов """
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call 'connect' or use the context manager.")
        with self.connection.cursor() as cur:
            cur.execute(query, params or {})
            self.connection.commit()

    def fetchall(self, query: SQL, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """ Выполняет SQL-запрос и возвращает все строки результата """
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call 'connect' or use the context manager.")
        with self.connection.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params or {})
            return cur.fetchall()

    def fetchone(self, query: SQL, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """ Выполняет SQL-запрос и возвращает одну строку результата """
        if self.connection is None:
            raise RuntimeError("Database connection is not established. Call 'connect' or use the context manager.")
        with self.connection.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params or {})
            return cur.fetchone()

    def __enter__(self):
        """ Для автоматического открытия подключения """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Для автоматического закрытия подключения """
        self.close()
