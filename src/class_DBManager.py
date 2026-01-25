import psycopg2


class DBManager:
    """Класс, который подключается к БД PostgreSQL и работает с ней"""

    def __init__(self, params: dict):
        """Инициализируем менеджер параметрами подключения"""
        self.params = params

    def __str__(self) -> str:
        """Метод показывает к какой бд подключен пользователь"""
        return f"DBManager(database={self.params.get('database')}, user={self.params.get('user')})"

    def adding_info_in_table(self, per_company: list[dict]) -> None:
        """Метод заполняет таблицы данными"""
        conn = psycopg2.connect(**self.params)

        # Очистка таблиц на случай, если они заполнены
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE public.companies CASCADE")
            conn.commit()

            # Заполнение данными
            for n in per_company:
                cur.execute(
                    """
                INSERT INTO public.companies (
                company_id, company_name, company_url
                )
                VALUES(%s, %s, %s)
                ON CONFLICT (company_id) DO NOTHING
                """,
                    (n["employer_id"], n["employer_name"], n["employer_url"]),
                )

                int_from = int(n.get("salary_from") or 0)
                int_to = int(n.get("salary_to") or 0)

                cur.execute(
                    """INSERT INTO public.vacancies (
                    company_id, vacancy_title, vacancy_url, vacancy_salary_from,
                    vacancy_salary_to, currency, requirements, responsibilities,
                    city, street, building, schedule, working_days,
                    experience, employment, employment_form)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        n["employer_id"],
                        n["title"],
                        n["alternate_url"],
                        int_from,
                        int_to,
                        n["currency"],
                        n["requirement"],
                        n["responsibility"],
                        n["city"],
                        n["street"],
                        n["building"],
                        n["schedule"],
                        n["name"],
                        n["experience"],
                        n["employment"],
                        n["employment_form"],
                    ),
                )
                conn.commit()

    def get_companies_and_vacancies_count(self) -> list:
        """Метод получает список всех компаний и количество вакансий у каждой компании"""
        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT companies.company_name, COUNT(vacancies.vacancy_title)
                    FROM public.companies
                    LEFT JOIN public.vacancies ON companies.company_id = vacancies.company_id
                    GROUP BY companies.company_name
                """
                )

                return cur.fetchall()  # type: ignore[no-any-return]

    def get_all_vacancies(self) -> list:
        """Метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT DISTINCT companies.company_name, vacancies.vacancy_title,
                    vacancies.vacancy_salary_from, vacancies.vacancy_salary_to, vacancies.currency,
                    vacancies.vacancy_url FROM public.companies
                    LEFT JOIN public.vacancies ON companies.company_id = vacancies.company_id
                    WHERE vacancies.vacancy_salary_from IS NOT NULL AND
                    vacancies.vacancy_salary_to IS NOT NULL
                    ORDER BY companies.company_name
                    """
                )

                return cur.fetchall()  # type: ignore[no-any-return]

    def get_avg_salary(self) -> list:
        """Метод получает среднюю зарплату по вакансиям"""
        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT DISTINCT companies.company_name, AVG(vacancies.vacancy_salary_from) AS avg_from,
                       AVG(vacancies.vacancy_salary_to) AS avg_to, vacancies.currency
                       FROM public.companies
                       LEFT JOIN public.vacancies ON companies.company_id = vacancies.company_id
                       WHERE vacancies.vacancy_salary_from IS NOT NULL OR
                       vacancies.vacancy_salary_to IS NOT NULL AND companies.company_id = vacancies.company_id
                       GROUP BY companies.company_name, vacancies.currency
                       """
                )

                return cur.fetchall()  # type: ignore[no-any-return]

    def get_vacancies_with_higher_salary(self) -> list:
        """Метод получает список всех вакансий, у которых зарплата выше средней
        по всем вакансиям"""
        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                SELECT companies.company_name, vacancies.vacancy_title
                FROM public.companies
                JOIN public.vacancies ON companies.company_id = vacancies.company_id
                WHERE vacancies.vacancy_salary_from > (
                    SELECT AVG(vacancy_salary_from) FROM public.vacancies
                    WHERE vacancy_salary_from > 0)
                ORDER BY vacancies.vacancy_salary_from DESC
                """
                )

                return cur.fetchall()  # type: ignore[no-any-return]

    def get_vacancies_with_keyword(self, filter_words: str) -> list:
        """Метод получает список всех вакансий, в названии которых содержатся
        переданные в метод слова, например python."""
        words = f"%{filter_words.strip()}%"

        with psycopg2.connect(**self.params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT vacancies.vacancy_title
                    FROM public.vacancies
                    WHERE vacancies.vacancy_title ILIKE %s
                    OR vacancies.requirements ILIKE %s
                    OR vacancies.responsibilities ILIKE %s
                    """,
                    (words, words, words),
                )

                return cur.fetchall()  # type: ignore[no-any-return]

    def close_connection(self) -> None:
        """Метод закрывает соединение в main"""
        with psycopg2.connect(**self.params) as conn:
            if conn:
                conn.close()
                print("Соединение с базой данных прекращено")
            else:
                print("Соединение с базой данных уже прекращено")
