import psycopg2
from loguru import logger

from dotenv import load_dotenv
import os


load_dotenv()


def create_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
        )
        logger.info("Connection is ok")
        return connection
    except Exception as e:
        logger.info(f"Error creating connection: {e}")
        return None
