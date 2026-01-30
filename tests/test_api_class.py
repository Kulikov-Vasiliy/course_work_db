import pytest
import requests_mock
import requests
from src.api_class import HeadHunterAPI


# --- Тесты инициализации ---

def test_init_default_text():
    api = HeadHunterAPI(search_query="")
    # Проверка работы инкапсуляции через доступ к защищенному атрибуту (для теста)
    assert api._HeadHunterAPI__text == "Введите запрос"


def test_init_params(hh_api):
    assert hh_api.currency == "RUR"
    assert hh_api._HeadHunterAPI__only_with_salary is True


# --- Тесты метода get_vacancies ---

def test_get_vacancies_success(hh_api):
    """Проверка парсинга всех полей при успешном ответе"""
    url = "https://api.hh.ru/vacancies"
    mock_data = {
        "items": [
            {
                "name": "Developer",
                "url": "http://api.hh.ru",
                "salary": {"from": 100, "to": 200, "currency": "USD"},
                "address": {"city": "Moscow", "street": "Arbat", "building": "1"},
                "schedule": {"name": "Full time"},
                "employer": {"id": "99", "name": "Google", "url": "http://google.com"},
                "snippet": {"requirement": "Python", "responsibility": "Coding"},
                "experience": {"name": "3-6 years"},
                "employment": {"name": "Full"},
                "employment_form": {"name": "Office"},
                "work_schedule_by_days": [{"name": "Mon"}, {"name": "Tue"}]
            }
        ]
    }

    with requests_mock.Mocker() as m:
        m.get(url, json=mock_data)
        result = hh_api.get_vacancies()

        assert len(result) == 1
        v = result[0]
        assert v["title"] == "Developer"
        assert v["salary_from"] == 100
        assert v["city"] == "Moscow"
        assert v["employer_name"] == "Google"
        assert "Mon" in v["name"]
        assert v["experience"] == "3-6 years"


def test_get_vacancies_empty_fields(hh_api):
    """Проверка работы, если API прислал пустые или None поля"""
    url = "https://api.hh.ru/vacancies"
    mock_data = {
        "items": [
            {
                "name": "Minimal",
                "salary": None,
                "address": None,
                "employer": {"id": "1", "name": "X", "url": "Y"},
                "employment_form": {"name": "Contract"}
            }
        ]
    }

    with requests_mock.Mocker() as m:
        m.get(url, json=mock_data)
        result = hh_api.get_vacancies()

        v = result[0]
        assert v["salary_from"] == "0"
        assert v["city"] == "Не указано"
        assert v["street"] == "Не указано"


def test_get_vacancies_http_errors(hh_api):
    """Проверка проброса исключений при специфических кодах ошибок"""
    url = "https://api.hh.ru/vacancies"

    with requests_mock.Mocker() as m:
        # Тестируем 403 ошибку
        m.get(url, status_code=403)
        with pytest.raises(requests.exceptions.HTTPError):
            hh_api.get_vacancies()


# --- Тесты метода vacancies_per_company ---

def test_vacancies_per_company_logic(hh_api):
    """Проверка формирования списка вакансий конкретной компании"""
    url = "https://api.hh.ru/vacancies"
    mock_data = {
        "items": [
            {
                "name": "Backend",
                "alternate_url": "http://hh.ru",
                "employer": {"id": "55"},
                "salary": {"from": 50, "to": None, "currency": "RUR"}
            }
        ]
    }

    with requests_mock.Mocker() as m:
        m.get(url, json=mock_data)
        # Передаем ID компании
        result = hh_api.vacancies_per_company(employer_ids=["55"])

        assert len(result) == 1
        assert result[0]["employer_id"] == "55"
        assert result[0]["salary_to"] == 0  # Проверка обработки 'or 0'


def test_vacancies_per_company_request_exception(hh_api):
    """Проверка обработки ConnectionError (метод должен вернуть [])"""
    url = "https://api.hh.ru/vacancies"

    with requests_mock.Mocker() as m:
        m.get(url, exc=requests.exceptions.ConnectTimeout)
        result = hh_api.vacancies_per_company()
        assert result == []


# --- Тест абстрактного класса ---

def test_abstract_class_instantiation():
    """Проверка, что нельзя создать объект абстрактного класса"""
    from src.api_class import AbstractAPI
    with pytest.raises(TypeError):
        AbstractAPI()
