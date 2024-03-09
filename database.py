import psycopg2

def create_connection(host, database, user, password):
    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        return connection
    except Exception as e:
        print(f"Error creating connection: {e}")
        return None