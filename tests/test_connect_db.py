import pytest
from unittest.mock import MagicMock, patch
from src.connect_db import encode, create_database, create_tables


# --- Тесты для функции encode ---

def test_encode_removes_database():
    params = {"host": "localhost", "user": "admin", "database": "my_db"}
    result = encode(params)
    assert "database" not in result
    assert result["host"] == "localhost"
    # Проверка, что исходный словарь не изменился (copy())
    assert "database" in params


def test_encode_removes_dbname():
    params = {"host": "localhost", "dbname": "my_db"}
    result = encode(params)
    assert "dbname" not in result
    assert result["host"] == "localhost"


def test_encode_no_db_keys():
    params = {"host": "localhost", "user": "admin"}
    result = encode(params)
    assert result == params


# --- Тесты для create_database (с моками) ---

@patch("psycopg2.connect")
def test_create_database_if_not_exists(mock_connect):
    # Настройка моков
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    # Имитируем, что базы данных НЕ существует (fetchone вернет None)
    mock_cur.fetchone.return_value = None

    db_name = "test_db"
    params = {"user": "postgres"}

    create_database(db_name, params)

    # Проверка: создалась ли база
    mock_cur.execute.assert_any_call(f"CREATE DATABASE {db_name}")
    assert mock_conn.autocommit is True
    mock_conn.close.assert_called_once()


@patch("psycopg2.connect")
def test_create_database_already_exists(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    # Имитируем, что база существует (fetchone вернет что-то)
    mock_cur.fetchone.return_value = (1,)

    create_database("test_db", {})

    # Проверка: CREATE DATABASE не должен вызываться
    for call in mock_cur.execute.call_args_list:
        assert "CREATE DATABASE" not in call[0][0]


# --- Тесты для create_tables (с моками) ---

@patch("psycopg2.connect")
def test_create_tables_success(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    # Используем __enter__ для контекстного менеджера with conn.cursor()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    create_tables({"dbname": "test_db"})

    # Проверяем, что были вызовы создания таблиц
    calls = [call[0][0] for call in mock_cur.execute.call_args_list]
    assert any("CREATE TABLE IF NOT EXISTS Companies" in c for c in calls)
    assert any("CREATE TABLE IF NOT EXISTS Vacancies" in c for c in calls)

    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("psycopg2.connect")
def test_create_tables_error_rollback(mock_connect):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    # Имитируем ошибку при работе курсора
    mock_conn.cursor.side_effect = Exception("SQL Error")

    # Проверяем, что функция не "падает", а обрабатывает исключение
    create_tables({})

    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()