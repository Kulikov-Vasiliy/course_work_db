import psycopg2


""""   for item in result.get("items", []):
            if item:
                # print(item)
                title = item.get("name")
                alternate_url = item.get("url")
                salary_info = item.get("salary", {})  # параметр устаревший
                if salary_info:
                    salary_from = salary_info.get("from")
                    salary_to = salary_info.get("to")
                    currency = salary_info.get("currency")
                else:
                    salary_from = "0"
                    salary_to = "0"
                    currency = ""
                address_info = item.get("address", {})
                if address_info:
                    city = address_info.get("city", "Не указано")
                    street = address_info.get("street", "Не указано")
                    building = address_info.get("building", "Не указано")
                else:
                    city = "Не указано"
                    street = "Не указано"
                    building = "Не указано"
                schedule_info = item.get("schedule", {})
                schedule = schedule_info.get("name", "Не указано")
                name = ""
                if item.get("work_schedule_by_days"):
                    for el in item.get("work_schedule_by_days"):
                        name += el.get("name", "Не указано")
                employer_info = item.get("employer")
                em_id = employer_info.get("id")
                em_name = employer_info.get("name")
                em_url = employer_info.get("url")
                # print(f"Полученные данные: {snippet}")
                snippet = item.get("snippet", {})
                requirement = snippet.get("requirement")
                responsibility = snippet.get("responsibility")
                # print(f"Требования: {requirement}, Обязанности: {responsibility}")
                experience_info = item.get("experience", {})
                experience = experience_info.get("name", "Без опыта или не требуется")
                employment_info = item.get("employment", {})
                employment = employment_info.get("name", "Не указано")
                employment_form_info = item.get("employment_form")
                employment_form = employment_form_info.get("name", "Не указана")

                wanted.append(
                    {
                        "title": title,
                        "alternate_url": alternate_url,
                        "salary_from": salary_from,
                        "salary_to": salary_to,
                        "currency": currency,
                        "city": city,
                        "street": street,
                        "building": building,
                        "schedule": schedule,
                        "name": name,
                        "employer_id": em_id,
                        "employer_name": em_name,
                        "employer_url": em_url,
                        "responsibility": responsibility,
                        "requirement": requirement,
                        "experience": experience,
                        "employment": employment,
                        "employment_form": employment_form,
                    }
                )"""
class DBManager:
    """Класс, который подключается к БД PostgreSQL и работает с ней"""

    def init(self,
        employer_name: str,
        employer_id: str,
        employer_url: str,
        title: str,
        url: str,
        salary_from: str,
        salary_to: str,
        currency: str | None,
        city: str,
        street: str,
        building: str,
        schedule: str,
        name: str,
        experience: str,
        employment: str,
        employment_form: str,
        requirement: str = "Требования не указаны",
        responsibility: str = "Обязанности не указаны",

    ) -> None:
        self.employer_name = employer_name
        self.employer_id = employer_id
        self.employer_url = employer_url
        self.title = title
        self.url = url
        self.salary_from = salary_from if salary_from else "0"
        self.salary_to = salary_to if salary_to else "0"
        self.currency = currency
        self.requirement = requirement
        self.responsibility = responsibility
        self.city = city
        self.street = street
        self.building = building
        self.schedule = schedule
        self.working_days = name
        # пара self.название_столбца_бд = ключ name(2/2 или 5/2) из апи-ответа
        self.experience = experience
        self.employment = employment
        self.employment_form = employment_form


    def get_companies_and_vacancies_count(self, wanted: list[dict], database_name: str, params: dict):
        """Метод получает список всех компаний и количество вакансий у каждой компании"""
        conn = psycopg2.connect(dbname=database_name, **params)

        with conn.cursor() as cur:
            for _ in wanted:
                cur.execute("""
                INSERT INTO Компании(
                employer_id, employer_name, employer_url
                )
                VALUES(%s, %s, %s)
                """,(
                self.employer_id, self.employer_name, self.employer_url))

                cur.execute(
                    """
                INSERT INTO Вакансии(
                vacancy_title,
                vacancy_url,
                vacancy_salary_from,
                vacancy_salary_to,
                currency,
                requirements,
                responsibilities,
                city,
                street,
                building,
                schedule,
                working_days,
                experience,
                employment,
                employment_form)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                        self.title,
                        self.url,
                        self.salary_from,
                        self.salary_to,
                        self.currency,
                        self.requirement,
                        self.responsibility,
                        self.city,
                        self.street,
                        self.building,
                        self.schedule,
                        self.working_days,
                        self.experience,
                        self.employment,
                        self.employment_form
                    ))
                conn.commit()

                cur.execute("""SELECT * FROM Компании""")
                cur.execute("""SELECT * FROM Вакансии""")
                conn.commit()
            conn.close()

    def get_all_vacancies(self):
        """Метод получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        pass

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