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
                INSERT INTO companies (
                company_id, company_name, company_url
                )
                VALUES(%s, %s, %s)
                ON CONFLICT (company_id) DO NOTHING
                """, (
                    n["employer_id"], n["employer_name"], n["employer_url"]
                ))

                cur.execute("""
                INSERT INTO vacancies (
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

    def get_companies_and_vacancies_count(self):
        """Метод получает список всех компаний и количество вакансий у каждой компании"""
        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT companies.company_name, COUNT(vacancies.vacancy_title)
                    FROM companies
                    LEFT JOIN vacancies ON companies.company_id = vacancies.company_id
                    GROUP BY companies.company_name
                """)
                # conn.commit()

                return cur.fetchall()

    def get_all_vacancies(self):
        """Метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:

                cur.execute("""SELECT DISTINCT companies.company_name, vacancies.vacancy_title,
                vacancies.vacancy_salary_from, vacancies.vacancy_salary_to, vacancies.currency,
                vacancies.vacancy_url FROM companies
                LEFT JOIN vacancies ON companies.company_id = vacancies.company_id
                WHERE vacancies.vacancy_salary_from IS NOT NULL AND
                vacancies.vacancy_salary_to IS NOT NULL
                ORDER BY companies.company_name
                """)
                conn.commit()

                return cur.fetchall()

    def get_avg_salary(self):
        """Метод получает среднюю зарплату по вакансиям"""
        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT DISTINCT companies.company_name, AVG(vacancies.vacancy_salary_from) AS avg_from,
                       AVG(vacancies.vacancy_salary_to) AS avg_to, vacancies.currency
                       FROM companies
                       LEFT JOIN vacancies ON companies.company_id = vacancies.company_id
                       WHERE vacancies.vacancy_salary_from IS NOT NULL OR
                       vacancies.vacancy_salary_to IS NOT NULL
                       ORDER BY companies.company_name
                       """)
                conn.commit()

                return cur.fetchall()


    def get_vacancies_with_higher_salary(self):
        """Метод получает список всех вакансий, у которых зарплата выше средней
         по всем вакансиям"""
        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT DISTINCT companies.company_name, vacancies.vacancy_title
                    FROM companies
                    JOIN vacancies ON companies.company_id = vacancies.company_id
                    WHERE vacancies.vacancy_salary_from AND vacancies.vacancy_salary_to IS NOT NULL
                    AND vacancies.vacancy_salary_from > AVG(vacancies.vacancy_salary_from)
                    OR vacancies.vacancy_salary_to > AVG(vacancies.vacancy_salary_to)
                    ORDER BY companies.company_name
                """)
                conn.commit()

                return cur.fetchall()


    def get_vacancies_with_keyword(self):
        """Метод получает список всех вакансий, в названии которых содержатся
        переданные в метод слова, например python."""
        pass
