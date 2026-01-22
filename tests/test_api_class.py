import unittest
from unittest.mock import Mock, patch

import requests

from src.api_class import HeadHunterAPI


class TestHeadHunterAPI(unittest.TestCase):
    """Тестирование класса HeadHunterAPI с использованием мокирования requests"""

    def setUp(self):
        self.hh_api = HeadHunterAPI(search_query="Python developer", only_with_salary=True)

    def test_init(self):
        """Проверка инициализации приватных атрибутов"""
        self.assertEqual(self.hh_api._HeadHunterAPI__text, "Python developer")
        self.assertTrue(self.hh_api._HeadHunterAPI__only_with_salary)
        self.assertEqual(self.hh_api.currency, "RUR")

    @patch("requests.get")
    def test_get_vacancies_success_parsing(self, mock_get):
        # Фиктивные данные, которые имитируют ответ hh.ru API
        mock_response_data = {
            "items": [
                {
                    "name": "Vacancy Title 1",
                    "url": "testurl.com",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUB"},
                    "address": {"city": "Moscow", "street": "Tverskaya", "building": "1"},
                    "schedule": {"name": "Full Time"},
                    "work_schedule_by_days": [{"name": "Mon"}, {"name": "Tue"}],
                    "employer": {"id": "123", "name": "Test Company", "url": "http://testcompany.com"},
                    "snippet": {"requirement": "Test Req", "responsibility": "Test Resp"},
                    "experience": {"name": "Between 1 and 3 years"},
                    "employment": {"name": "Full"},
                    "employment_form": {"name": "Staff"},
                }
            ],
            "found": 1,
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response

        # Вызываем тестируемый метод
        result_list = self.hh_api.get_vacancies()

        # Проверяем, что вернулся список словарей и его длина верна
        self.assertIsInstance(result_list, list)
        self.assertEqual(len(result_list), 1)

        # Проверяем структуру и значения первого элемента
        first_vacancy = result_list[0]
        self.assertEqual(first_vacancy["title"], "Vacancy Title 1")
        self.assertEqual(first_vacancy["salary_from"], 100000)
        self.assertEqual(first_vacancy["city"], "Moscow")
        self.assertEqual(first_vacancy["name"], "MonTue")  # Склеенные дни

    @patch("requests.get")
    def test_get_vacancies_empty_result(self, mock_get):
        """Тестирование, когда API возвращает пустой список items"""
        mock_response_data = {"items": [], "found": 0}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response

        result_list = self.hh_api.get_vacancies()
        self.assertEqual(result_list, [])

    @patch("requests.get")
    def test_get_vacancies_http_error_404_raises(self, mock_get):
        """Тестирование, что ошибки HTTP выбрасываются (raise)"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        # Ожидаем, что вызов get_vacancies выбросит исключение HTTPError
        with self.assertRaises(requests.exceptions.HTTPError):
            self.hh_api.get_vacancies()

    @patch("requests.get")
    def test_get_vacancies_http_error_400_raises(self, mock_get):
        """Тестирование, что ошибка 400 выбрасывается"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        with self.assertRaises(requests.exceptions.HTTPError):
            self.hh_api.get_vacancies()
