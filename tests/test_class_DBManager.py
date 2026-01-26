import pytest
from unittest.mock import MagicMock, patch
from src.class_DBManager import DBManager


def test_init(manager, db_params):
    assert manager.params == db_params


def test_str(manager):
    assert str(manager) == "DBManager(database=test_db, user=test_user)"


@patch("psycopg2.connect")
def test_adding_info_in_table(mock_connect, manager):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    test_data = [{
        "employer_id": "1",
        "employer_name": "Company",
        "employer_url": "url",
        "title": "Dev",
        "alternate_url": "v_url",
        "salary_from": 100,
        "salary_to": 200,
        "currency": "RUB",
        "requirement": "req",
        "responsibility": "resp",
        "city": "City",
        "street": "Street",
        "building": "1",
        "schedule": "full",
        "name": "working days",
        "experience": "none",
        "employment": "full",
        "employment_form": "office"
    }]

    manager.adding_info_in_table(test_data)

    # Проверка очистки таблицы
    mock_cur.execute.assert_any_call("TRUNCATE TABLE public.companies CASCADE")
    # Проверка вставки в компании
    assert "INSERT INTO public.companies" in mock_cur.execute.call_args_list[1][0][0]
    # Проверка вставки в вакансии
    assert "INSERT INTO public.vacancies" in mock_cur.execute.call_args_list[2][0][0]
    # Проверка коммита
    assert mock_conn.commit.called


@patch("psycopg2.connect")
def test_get_companies_and_vacancies_count(mock_connect, manager):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    mock_cur.fetchall.return_value = [("Google", 10), ("Yandex", 5)]

    result = manager.get_companies_and_vacancies_count()

    assert len(result) == 2
    assert result[0][0] == "Google"
    assert "COUNT(vacancies.vacancy_title)" in mock_cur.execute.call_args[0][0]


@patch("psycopg2.connect")
def test_get_avg_salary(mock_connect, manager):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    mock_cur.fetchall.return_value = [("Google", 100000, 150000, "RUR")]

    result = manager.get_avg_salary()

    assert result[0][0] == "Google"
    assert "AVG(vacancies.vacancy_salary_from)" in mock_cur.execute.call_args[0][0]


@patch("psycopg2.connect")
def test_get_vacancies_with_keyword(mock_connect, manager):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    manager.get_vacancies_with_keyword("python")

    # Проверка передачи параметров в SQL запрос (процентные знаки для LIKE)
    args, kwargs = mock_cur.execute.call_args
    assert args[1] == ("%python%", "%python%", "%python%")
    assert "ILIKE %s" in args[0]


@patch("psycopg2.connect")
def test_close_connection(mock_connect, manager):
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn

    manager.close_connection()

    mock_conn.close.assert_called_once()
