import os
from configparser import ConfigParser


def config(filename: str = "database.ini", section: str = "postgresql") -> dict:
    # ПРОВЕРКА: существует ли файл физически?
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл {filename} не найден по пути: {os.path.abspath(filename)}")
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} is not found in the {filename} file.")
    return db
