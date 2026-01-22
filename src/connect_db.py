import psycopg2


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных"""

    # Создание бд
    conn = psycopg2.connect(dbname='python_cw', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"CREATE DATABASE {database_name} IF NOT EXISTS")

    conn.close()


def create_tables(database_name: str, params: dict) -> None:
    """ Создание таблиц для сохранения данных"""
    conn = psycopg2.connect(dbname=database_name, **params)

    try:
        # Создание курсора
        with conn.cursor() as cur:
            # Выполнение команды создания схемы
            cur.execute("CREATE TABLE Компании IF NOT EXISTS;")
            cur.execute("CREATE TABLE Вакансии IF NOT EXISTS;")

        # Сохранение изменений (COMMIT)
        conn.commit()
        print("Таблицы успешно создана")

    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()  # Откат изменений при ошибке
    finally:
        conn.close()