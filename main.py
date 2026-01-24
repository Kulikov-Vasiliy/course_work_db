# Функция для взаимодействия с пользователем
import psycopg2
import requests

from src.api_class import HeadHunterAPI
from src.class_DBManager import DBManager
from src.config import config
from src.connect_db import create_database, create_tables
from src.json_class import DATA_PATH, JSONSaver
from src.utils import (
    filter_vacancies,
    get_top_vacancies,
    get_vacancies_by_salary,
    print_vacancies,
    sort_vacancies,
)
from src.vacancy import Vacancy

path_file = DATA_PATH


def user_interaction() -> None:
    platforms = ["HeadHunter"]  # noqa F841
    # search_query = input("Введите поисковый запрос: ")
    search_query = "Python-разработчик"
    # with_salary = input("Показывать вакансии только с указанной зарплатой? Yes/No ").strip().upper()[0]
    with_salary = "Y"
    # top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    top_n = 3
    # filter_words = input("Введите ключевые слова для фильтрации вакансий: ").split()
    filter_words = "Python Django"
    # salary_range = input("Введите диапазон зарплат: ") # Пример: 100000 - 150000
    salary_range = "10000 - 300000"

    try:
        # Пример использования HeadHunterAPI
        hh_api = HeadHunterAPI(
            search_query=search_query,
            only_with_salary=True if with_salary == "Y" else False,
        )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print("400\nПараметры переданы с ошибкой")
        elif e.response.status_code == 403:
            print("403\nТребуется ввести капчу")
        elif e.response.status_code == 404:
            print("404\nУказанная вакансия не существует")

    else:
        hh_vacancies_json = hh_api.get_vacancies()

        # Преобразование набора данных из JSON в список объектов
        vacancies_list = Vacancy.cast_to_object_list(hh_vacancies_json)
        # for vac in vacancies_list[:top_n]:
        #     print(vac)

        filtered_vacancies = filter_vacancies(vacancies_list, filter_words)
        # print(filtered_vacancies)

        ranged_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)
        # print(ranged_vacancies)

        sorted_vacancies = sort_vacancies(ranged_vacancies)
        top_vacancies = get_top_vacancies(sorted_vacancies, top_n)
        print_vacancies(top_vacancies)

        # Сохранение информации о вакансиях в файл
        json_saver = JSONSaver(filename=path_file)
        json_saver.add_vacancy(vacancies_list)
        json_saver.delete_vacancy(vacancies_list)

        # Обработка информации через бд
        # 1. Получаем параметры из .ini (там обычно база 'postgres' или 'python_cw')
        params = config()
        target_db = "python_cw"

        # 2. Создаем БД
        # Передаем params, но внутри create_database нужно подключиться к 'postgres'
        create_database(target_db, params)

        # 3. Обновляем параметры подключения, чтобы работать с НОВОЙ базой
        params["database"] = target_db

        # 4. Создаем таблицы в новой базе
        # Теперь передаем обновленные параметры
        create_tables(params)

        # 5.  Инициализируем класс для работы с БД
        db_manager = DBManager(params)
        hh_vacancies_per_employer = hh_api.vacancies_per_company()
        db_manager.adding_info_in_table(hh_vacancies_per_employer)

        try:
            # # код для поиска возникшей ошибки
            # print("Проверка 1: count")
            # db_count = db_manager.get_companies_and_vacancies_count()
            #
            # print("Проверка 2: all")
            # db_all = db_manager.get_all_vacancies()
            #
            # print("Проверка 3: avg")
            # db_avg = db_manager.get_a
            #
            # print("Проверка 4: high")
            # db_avg = db_manager.get_vacancies_with_higher_salary()

            # print("Проверка 5: word")
            # db_avg = db_manager.get_vacancies_with_keyword(filter_words)

            # рабочий код:
            db_count = db_manager.get_companies_and_vacancies_count()
            for row in db_count:
                print(f"Компании: {row[0]}, всего вакансий: {row[1]}")

            db_all = db_manager.get_all_vacancies()
            for row in db_all:
                print(
                    f"""
В компании {row[0]}:
  * вакансия: {row[1]},
  * зп: {row[2]} - {row[3]} {row[4]},
  * ссылка на вакансию: {row[5]}
"""
                )
            db_avg = db_manager.get_avg_salary()
            for row in db_avg:
                print(f"Средняя зп в компании {row[0]}: {row[1]:.2f} - {row[2]:.2f} {row[3]}")
            db_high = db_manager.get_vacancies_with_higher_salary()
            for v in db_high:
                print(f"Компания: {v[0]}, Вакансия: {v[1]}")

            db_keyword = db_manager.get_vacancies_with_keyword(filter_words)
            for v in db_keyword:
                print("По запросу найдены вакансии")
                print(f"  * {v}")  # вакансии, содержащие искомые слова
                # из замены пользовательского ввода не попали таблицу

        except psycopg2.Error as e:
            print("--- Ошибка базы данных ---")
            print(f"Сообщение: {e.pgerror}")  # Полный текст ошибки от PostgreSQL
            print(f"Код ошибки: {e.pgcode}")  # Код (например, '42P01' для UndefinedTable)
            # Диагностика (особенно полезно при UndefinedColumn)
            if e.diag.message_primary:
                print(f"Суть: {e.diag.message_primary}")
                print(f"Где именно: {e.diag.column_name or 'не указано'}")
        except Exception as e:
            print(f"Тип ошибки: {type(e)}")
            print(f"Текст ошибки: {e}")


if __name__ == "__main__":
    user_interaction()
