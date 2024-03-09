import json
import datetime
from database import create_connection


changes_log = []

def process_document(connection):
    try:
        cursor = connection.cursor()

        # Получаем первый необработанный документ с типом transfer_document
        cursor.execute("SELECT * FROM public.documents WHERE processed_at IS NULL AND document_type = 'transfer_document' ORDER BY recieved_at ASC LIMIT 1")
        document = cursor.fetchone()

        if document:
            # Извлекаем данные из JSON
            document_data = document[3]

            # Извлекаем объекты из документа
            objects = document_data.get('objects', [])

            # Собираем полный список объектов из таблицы data
            objects_in_data = set()
            for obj in objects:
                objects_in_data.add(obj)

                # Добавляем связанные дочерние объекты
                cursor.execute("SELECT object FROM public.data WHERE parent = %s", (obj,))
                children = cursor.fetchall()
                objects_in_data.update(child[0] for child in children)

            # Обрабатываем объекты в соответствии с условиями блока operation_details
            if 'operation_details' in document_data:
                operation_details = document_data['operation_details']

                for obj in objects_in_data:
                    data_update_query = "UPDATE public.data SET "
                    updates = []

                    for field, values in operation_details.items():
                        old_value = values.get('old')
                        new_value = values.get('new')

                        updates.append(f"{field} = '{new_value}'")

                    if updates:
                        data_update_query += ", ".join(updates)
                        data_update_query += f" WHERE object = '{obj}'"

                        cursor.execute(data_update_query)

            for field, values in operation_details.items():
                old_value = values.get('old')
                new_value = values.get('new')

                updates.append(f"{field} = '{new_value}'")
    
            # Добавляем информацию об изменениях в лог
            changes_log.append(f"Object '{obj}': {field} changed from '{old_value}' to '{new_value}'")

            # Обновляем отметку времени в поле processed_at
            cursor.execute("UPDATE public.documents SET processed_at = %s WHERE doc_id = %s",
                           (datetime.datetime.now(), document[0]))

            # Фиксируем изменения
            connection.commit()

            return True
        else:
            return False
    except Exception as e:
        print(f"Error processing document: {e}")
        return False
    finally:
        cursor.close()


if __name__ == '__main__':
    connection = create_connection(host="localhost", database="znak", user="postgres", password="postgres")

    if connection:
        success = process_document(connection)
        for change in changes_log:
            print(change)
        if success:
            print("Document processed successfully")
        else:
            print("Error processing document")

        connection.close()
