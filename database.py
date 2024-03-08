import psycopg2
from loguru import logger


def create_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="znak",
            user="postgres",
            password="postgres"
        )
        logger.info("Successfully connected to the database.")
        
        return connection

    except Exception as e:
        logger.error(f"Error while creating connection: {e}")
        return None

