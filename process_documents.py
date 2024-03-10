import json
import datetime
from database import create_connection
from loguru import logger

"""Переменная для проверки работоспособности скрипта."""
# changes_log = []


def execute_query(cursor, query, params=None):
    cursor.execute(query, params)
    return cursor.fetchall() if cursor.description else None


def update_data(cursor, obj, operation_details):
    updates = []
    for field, values in operation_details.items():
        old_value = values.get("old")
        new_value = values.get("new")
        updates.append(f"{field} = '{new_value}'")

    if updates:
        updates_query = ", ".join(updates)
        cursor.execute(f"UPDATE public.data SET {updates_query} WHERE object = '{obj}'")


def process_document(connection):
    try:
        cursor = connection.cursor()

        documents_query = "SELECT * FROM public.documents WHERE processed_at IS NULL AND document_type = 'transfer_document' ORDER BY recieved_at ASC LIMIT 1"
        documents = execute_query(cursor, documents_query)

        logger.info("Получаем первый необработанный документ с типом transfer_document")

        if documents:
            document = documents[0]
            document_data = document[3]
            objects = document_data.get("objects", [])
            objects_in_data = set()

            for obj in objects:
                objects_in_data.add(obj)
                children_query = "SELECT object FROM public.data WHERE parent = %s"
                children = execute_query(cursor, children_query, (obj,))
                logger.info("Добавляем связанные дочерние объекты")
                objects_in_data.update(child[0] for child in children)

            if "operation_details" in document_data:
                for obj in objects_in_data:
                    update_data(cursor, obj, document_data["operation_details"])

            update_documents_query = (
                "UPDATE public.documents SET processed_at = %s WHERE doc_id = %s"
            )
            cursor.execute(
                update_documents_query, (datetime.datetime.now(), document[0])
            )
            logger.info("Обновляем отметку времени в поле processed_at")

            connection.commit()
            return True

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return False

    finally:
        cursor.close()


if __name__ == "__main__":
    connection = create_connection()
    if connection:
        success = process_document(connection)
        # for change in changes_log:
        #     print(change)
        if success:
            logger.info("Document processed successfully")
        else:
            logger.info("Error processing document")

        connection.close()
