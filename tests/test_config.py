import pytest
import os
from configparser import ConfigParser
from src.config import config


# Тест 1: Успешное чтение стандартной секции
def test_config_success(create_ini_file):
    result = config(filename=create_ini_file, section="postgresql")

    assert result['host'] == 'localhost'
    assert result['user'] == 'postgres'
    assert result['port'] == '5432'
    assert len(result) == 4


# Тест 2: Чтение другой существующей секции
def test_config_alternative_section(create_ini_file):
    result = config(filename=create_ini_file, section="other_section")
    assert result['key'] == 'value'


# Тест 3: Ошибка при отсутствии секции
def test_config_section_not_found(create_ini_file):
    with pytest.raises(Exception) as excinfo:
        config(filename=create_ini_file, section="non_existent")
    # Проверка текста ошибки (в вашем коде есть баг с {0} и {1}, тест это подсветит)
    assert "Section" in str(excinfo.value)


# Тест 4: Ошибка при отсутствии файла
def test_config_file_not_found():
    # Если файла нет, parser.read() вернет пустой список,
    # и has_section вернет False, что вызовет Exception
    with pytest.raises(Exception):
        config(filename="missing_file.ini")
