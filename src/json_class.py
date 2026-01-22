import json
import os
import pathlib
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.vacancy import Vacancy

BASE_DIR = pathlib.Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "vacancies.json"


class AbstractJSONSaver(ABC):
    """Абстрактный класс для сохранения данных о вакансиях в файл и работы с ними"""

    @abstractmethod
    def add_vacancy(self, vacancy_data: List[Vacancy]) -> None:
        """Метод для добавления списка объектов Vacancy в файл."""
        pass

    @abstractmethod
    def get_vacancies(self, criteria: Optional[Dict[str, Any]] = None) -> List[Vacancy]:
        """Метод для получения данных из файла по указанным критериям."""
        pass

    @abstractmethod
    def delete_vacancy(self, vacancies_to_delete: List[Vacancy]) -> None:
        """Метод для удаления списка объектов Vacancy из файла."""
        pass


class JSONSaver(AbstractJSONSaver):
    """
    Класс для сохранения вакансий в json-файл и их удаления из него.
    Работает с объектами класса Vacancy.
    """

    def __init__(self, filename: pathlib.Path = DATA_PATH) -> None:
        self.filename = filename
        # Убедимся, что директория существует
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        # Убедимся, что файл существует или создан с пустым списком
        if not self.filename.exists() or os.stat(self.filename).st_size == 0:
            self.__write_data([])

    def __read_data(self) -> List[Dict[str, Any]]:
        """Внутренний метод для чтения данных из файла."""
        with open(self.filename, "r", encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]

    def __write_data(self, data: List[Dict[str, Any]]) -> None:
        """Внутренний метод для записи данных в файл."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_vacancy(self, vacancy_list: List[Vacancy]) -> None:
        """Логика добавления списка объектов Vacancy в файл."""
        data = self.__read_data()
        # Преобразуем объекты Vacancy в словари перед сохранением
        vac_dicts = [JSONSaver.__vacancy_to_dict(vac) for vac in vacancy_list]
        data.extend(vac_dicts)
        self.__write_data(data)

    def get_vacancies(  # type: ignore[override]
            self, criteria: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        # Этот метод возвращает list[dict] из файла, что корректно по логике
        data = self.__read_data()
        if criteria is None:
            return data

        filtered_data = [item for item in data if all(item.get(key) == value for key, value in criteria.items())]
        return filtered_data

    def delete_vacancy(self, vacancies_to_delete: List[Vacancy]) -> None:
        """Удаление информации о вакансиях из файла по списку объектов Vacancy (по URL)."""
        data = self.__read_data()
        initial_count = len(data)

        urls_to_delete = {vac.url for vac in vacancies_to_delete}

        # Оставляем только те элементы, URL которых нет в списке на удаление
        filtered_data = [item for item in data if item.get("url") not in urls_to_delete]

        self.__write_data(filtered_data)
        deleted_count = initial_count - len(filtered_data)
        print(f"Удалено {deleted_count} вакансий из {self.filename}")

    @staticmethod
    def __vacancy_to_dict(vacancy_obj: Vacancy) -> Dict[str, Any]:
        """Преобразует объект Vacancy в словарь для записи в JSON."""
        return {
            "title": vacancy_obj.title,
            "url": vacancy_obj.url,
            "salary_from": vacancy_obj.salary_from,
            "salary_to": vacancy_obj.salary_to,
            "currency": vacancy_obj.currency,
            "requirement": vacancy_obj.requirement,
            "responsibility": vacancy_obj.responsibility,
        }
