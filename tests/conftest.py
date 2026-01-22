import pathlib

import pytest

from src.json_class import JSONSaver
from src.vacancy import Vacancy


@pytest.fixture
def sample_vacancies_list_objects():
    """Возвращает список объектов Vacancy для тестирования всех функций"""
    return [
        Vacancy(
            "Python Developer (Mid)",
            "url1",
            "100000",
            "150000",
            "RUR",
            requirement="Linux, Docker, Git",
            responsibility="Develop",
        ),
        Vacancy(
            "Java Developer (Senior)",
            "url2",
            "120000",
            "180000",
            "RUR",
            requirement="Spring",
            responsibility="Develop back",
        ),
        Vacancy("QA Engineer (Junior)", "url3", "50000", "80000", "RUR"),
        Vacancy("DevOps Engineer (Lead)", "url4", "130000", "160000", "RUR"),
        Vacancy("Junior Intern", "url5", "0", "0", None),  # Вакансия без ЗП
        Vacancy("Sales Manager", "url6", "80000", "0", "RUR"),  # ЗП от
        Vacancy("Cleaner", "url7", "0", "40000", "RUR"),  # ЗП до
    ]


@pytest.fixture
def actual_titles():
    return [
        "Sales Manager",
        "DevOps Engineer (Lead)",
        "Java Developer (Senior)",
        "Python Developer (Mid)",
    ]


@pytest.fixture
def sample_vacancies_list():
    """Возвращает список реальных объектов Vacancy для тестирования"""
    return [
        Vacancy("Python Developer", "http://url.com/p", "100000", "150000", "RUR"),
        Vacancy("Java Developer", "http://url.com/j", "120000", "180000", "RUR"),
        Vacancy("QA Engineer", "http://url.com/q", "50000", "80000", "RUR"),
    ]


@pytest.fixture
def temp_json_saver(tmp_path):
    """
    Создает временный JSON файл и инициализирует JSONSaver для тестов.
    tmp_path - это встроенная фикстура pytest для временных директорий.
    """
    test_file: pathlib.Path = tmp_path / "test_vacancies.json"
    saver = JSONSaver(filename=test_file)
    return saver
