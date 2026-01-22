import psycopg2


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных"""
    conn_params = params.copy()
    if 'database' in conn_params:
        del conn_params['database']
    if 'dbname' in conn_params:
        del conn_params['dbname']

    conn = psycopg2.connect(dbname='python_cw', **conn_params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"CREATE DATABASE {database_name} IF NOT EXISTS")

    conn.close()


def create_tables(database_name: str, conn_params: dict) -> None:
    """ Создание таблиц для сохранения данных"""
    # conn_params = params.copy()
    # if 'database' in conn_params:
    #     del conn_params['database']
    # if 'dbname' in conn_params:
    #     del conn_params['dbname']

    conn = psycopg2.connect(dbname=database_name, **conn_params)

    try:
        # Создание курсора
        with conn.cursor() as cur:
            # Выполнение команды создания таблиц

            cur.execute("""CREATE TABLE Компании(
            company_id text PRIMARY KEY,
            company_name text NOT NULL,
            company_url text NOT NULL
            ) IF NOT EXISTS;""")

            cur.execute("""CREATE TABLE Вакансии(
            vacancy_№ serial,
            employer text REFERENCES Компании(company_id) NOT NULL,
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
            ) IF NOT EXISTS;""")

        # Сохранение изменений (COMMIT)
        conn.commit()
        print("Таблицы успешно созданы")

    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()  # Откат изменений при ошибке
    finally:
        conn.close()