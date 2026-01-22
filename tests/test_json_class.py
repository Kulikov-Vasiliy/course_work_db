import json
from io import StringIO
from unittest.mock import patch

import pytest

from src.json_class import AbstractJSONSaver, JSONSaver


class TestJSONSaver:

    def test_instantiation_creates_file(self, tmp_path):
        """Проверка, что файл создается при инициализации, если его нет"""
        temp_file = tmp_path / "new_file.json"
        assert not temp_file.exists()

        saver = JSONSaver(filename=temp_file) # noqa F841
        assert temp_file.exists()
        # Проверяем, что файл инициализирован пустым списком
        with open(temp_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data == []

    def test_add_vacancy(self, temp_json_saver, sample_vacancies_list):
        """Проверка добавления одной вакансии"""
        vac_to_add = sample_vacancies_list[:1]  # Берем только первую вакансию
        temp_json_saver.add_vacancy(vac_to_add)

        # Читаем данные напрямую для проверки внутреннего состояния
        data = temp_json_saver._JSONSaver__read_data()
        assert len(data) == 1
        assert data[0]["title"] == "Python Developer"
        assert data[0]["url"] == "http://url.com/p"

    def test_add_multiple_vacancies(self, temp_json_saver, sample_vacancies_list):
        """Проверка добавления нескольких вакансий"""
        temp_json_saver.add_vacancy(sample_vacancies_list)

        data = temp_json_saver._JSONSaver__read_data()
        assert len(data) == 3
        assert data[-1]["title"] == "QA Engineer"  # Проверяем последний добавленный элемент

    def test_get_vacancies_all(self, temp_json_saver, sample_vacancies_list):
        """Проверка получения всех вакансий"""
        temp_json_saver.add_vacancy(sample_vacancies_list)
        vacancies_data = temp_json_saver.get_vacancies()
        assert len(vacancies_data) == 3
        # Проверяем первый элемент полученного списка словарей
        assert vacancies_data[0]["title"] == "Python Developer"

    def test_get_vacancies_with_criteria(self, temp_json_saver, sample_vacancies_list):
        """Проверка получения вакансий по критериям"""
        temp_json_saver.add_vacancy(sample_vacancies_list)

        # Фильтруем по названию
        criteria = {"title": "Java Developer"}
        filtered = temp_json_saver.get_vacancies(criteria=criteria)

        assert len(filtered) == 1
        assert filtered[0]["title"] == "Java Developer"

    @patch("sys.stdout", new_callable=StringIO)  # Используем StringIO для более чистого захвата вывода
    def test_delete_vacancy(self, mock_stdout, temp_json_saver, sample_vacancies_list):
        """Проверка удаления вакансий по списку объектов и подсчета удаленных"""
        temp_json_saver.add_vacancy(sample_vacancies_list)
        assert len(temp_json_saver.get_vacancies()) == 3

        vacs_to_delete = sample_vacancies_list[1:]  # Удаляем Java и QA
        temp_json_saver.delete_vacancy(vacs_to_delete)

        data = temp_json_saver.get_vacancies()
        assert len(data) == 1
        titles = sorted([item["title"] for item in data])
        assert titles == ["Python Developer"]

        output = mock_stdout.getvalue()
        assert "Удалено 2 вакансий из" in output

    def test_abstract_class_instantiation(self):
        """Проверка, что AbstractJSONSaver нельзя инстанцировать напрямую"""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            AbstractJSONSaver()
