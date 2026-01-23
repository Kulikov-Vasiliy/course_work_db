import psycopg2


class DBManager:
    """Класс, который подключается к БД PostgreSQL и работает с ней"""

    def __init__(self, params: dict):
        """Инициализируем менеджер параметрами подключения"""
        self.params = params

    def __str__(self) -> str:
        """Метод показывает к какой бд подключен пользователь"""
        return f"DBManager(database={self.params.get('database')}, user={self.params.get('user')})"

    def adding_info_in_table(self, wanted: list[dict]) -> None:
        """Метод заполняет таблицы данными"""
        conn = psycopg2.connect(**self.params)

        # Очистка таблиц на случай, если они заполнены
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE Companies CASCADE")
            conn.commit()

            # Заполнение данными
            for n in wanted:
                cur.execute("""
                INSERT INTO Companies(
                company_id, company_name, company_url
                )
                VALUES(%s, %s, %s)
                ON CONFLICT (company_id) DO NOTHING
                """, (
                    n["employer_id"], n["employer_name"], n["employer_url"]
                ))

                cur.execute("""
                INSERT INTO Vacancies(
                company_id, vacancy_title,
                vacancy_url, vacancy_salary_from,
                vacancy_salary_to,  currency,
                requirements, responsibilities,
                city, street, building, schedule,
                working_days, experience, employment,
                employment_form)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    n["employer_id"], n["title"], n["url"], n["salary_from"],
                    n["salary_to"], n["currency"], n["requirement"], n["responsibility"],
                    n["city"], n["street"], n["building"], n["schedule"], n["working_days"],
                    n["experience"], n["employment"], n["employment_form"]
                ))
        conn.commit()
        # conn.close()

    def get_companies_and_vacancies_count(self):
        """Метод получает список всех компаний и количество вакансий у каждой компании"""
        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT Companies.company_name, COUNT(Vacancies.vacancy_title)
                    FROM Companies
                    LEFT JOIN Vacancies ON Companies.company_id = Vacancies.company_id
                    GROUP BY Companies.company_name
                """)
                # conn.commit()

                return cur.fetchall()

    def get_all_vacancies(self):
        """Метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:

                cur.execute("""SELECT * FROM Компании""")
                # cur.execute("""SELECT * FROM Вакансии""")
                conn.commit()

        conn.close()


    def get_avg_salary(self):
        """Метод получает среднюю зарплату по вакансиям"""
        pass


    def get_vacancies_with_higher_salary(self):
        """Метод получает список всех вакансий, у которых зарплата выше средней
         по всем вакансиям"""
        pass


    def get_vacancies_with_keyword(self):
        """Метод получает список всех вакансий, в названии которых содержатся
        переданные в метод слова, например python."""
        pass
