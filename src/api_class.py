# from enum import Enum, auto
import os
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv

load_dotenv()
CURRENCY_API = os.getenv("API_KEY_CURRENCY")

#
# class Experience(Enum):
#     NO_EXPERIENCE = "Без опыта"
#     LESS_THAN_1 = "Менее 1 года"
#     ONE_TO_THREE = "от 1 года до 3 лет"
#     THREE_TO_SIX = "от 3 до 6 лет"
#     MORE_THAN_SIX = "Более 6 лет"
#
#
# class Employment(Enum):
#     CIVIL_CONTRACT = "ГПХ"
#     SELF_EMPLOYED = "Самозанятость"
#     OFFICIAL_EMPLOYMENT = "Официальное трудоустройство"
#     SERVICE_CONTRACT = "Договор подряда"
#
#
# class Currency(Enum):
#     EUR = "Eur"
#     RUB = "Rub"
#     USD = "Usd"
#
#
# # Создайте словарь для сопоставления значений образования
# EDUCATION_LEVELS = {
#     "Не требуется или не указано": "not_required_or_not_specified",
#     "Среднее-специальное": "special_secondary",
#     "Высшее": "higher"
# }


class AbstractAPI(ABC):
    """Абстрактный класс для работы с апи"""

    @abstractmethod
    def get_vacancies(self):  # type: ignore[no-untyped-def]
        return self.__get_vacancies()


class HeadHunterAPI(AbstractAPI):
    """
    Класс для работы с платформой hh.ru:
    должен уметь подключаться к API и получать вакансии
    """

    search_query: str
    only_with_salary: bool
    no_magic: bool

    def __init__(
        self,
        search_query: str,
        currency: str = "RUR",
        only_with_salary: bool = False,
        no_magic: bool = True,
    ):
        self.__text = search_query if search_query != "" else "Введите запрос"
        self.__only_with_salary = only_with_salary if only_with_salary is True else False
        self.currency = currency
        self.__no_magic = no_magic

    def get_vacancies(self):  # type: ignore[no-untyped-def]
        """Подключение к api и получение вакансий с фильтрацией"""
        wanted = []

        try:
            __url = "https://api.hh.ru/vacancies"
            __payload = {
                "text": self.__text,
                "only_with_salary": self.__only_with_salary,
                "no_magic": self.__no_magic,
            }
            response = requests.get(__url, params=__payload)
            response.raise_for_status()
            result = response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                raise
            elif e.response.status_code == 403:
                raise
            elif e.response.status_code == 404:
                raise
            else:
                raise

        for item in result.get("items", []):
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
                )

        if not wanted:
            return []
        return wanted
