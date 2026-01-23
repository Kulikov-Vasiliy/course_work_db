import psycopg2


def encode(params: dict) -> dict:
    """Попытка решить проблему с кодировкой .ini"""
    print(f"Тип params: {type(params)}")
    print(f"Содержимое params: {params}")

    conn_params = params.copy()
    if 'database' in conn_params:
        del conn_params['database']
    elif 'dbname' in conn_params:
        del conn_params['dbname']

    return conn_params


def create_database(database_name: str, conn_params: dict) -> None:
    """Создание базы данных"""
    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cur = conn.cursor()

    # Проверяем наличие базы данных
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (database_name,))
    exists = cur.fetchone()

    if not exists:
        # В PostgreSQL нельзя использовать IF NOT EXISTS в CREATE DATABASE
        # Поэтому используем обычный запрос после проверки
        cur.execute(f"CREATE DATABASE {database_name}")
        print(f"База данных {database_name} создана.")
    else:
        print(f"База данных {database_name} уже существует.")
    conn.close()


def create_tables(conn_params: dict) -> None:
    """ Создание таблиц для сохранения данных"""
    conn = psycopg2.connect(**conn_params)

    try:
        # Создание курсора
        with conn.cursor() as cur:
            # Выполнение команды создания таблиц
            cur.execute("""CREATE TABLE IF NOT EXISTS Companies(
            company_id text PRIMARY KEY,
            company_name text NOT NULL,
            company_url text NOT NULL
            );""")

            cur.execute("""CREATE TABLE IF NOT EXISTS Vacancies(
            vacancy_num serial,
            company_id text REFERENCES Companies(company_id) NOT NULL,
            vacancy_title text NOT NULL,
            vacancy_url text NOT NULL,
            vacancy_salary_from text,
            vacancy_salary_to text,
            currency char(3),
            requirements text,
            responsibilities text,
            city text,
            street text,
            building text,
            schedule text,
            working_days text,
            experience text,
            employment text,
            employment_form text
            );""")
        # Сохранение изменений (COMMIT)
        conn.commit()
        print("Таблицы успешно созданы")

    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()  # Откат изменений при ошибке
    finally:
        conn.close()
