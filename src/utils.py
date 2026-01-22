from src.vacancy import Vacancy


def filter_vacancies(vacancies_list: list[Vacancy], filter_words: str) -> list[Vacancy]:
    """Фильтрует вакансии по ключевым словам"""
    if not filter_words:
        return []

    result = []
    words_list = [word.lower() for word in filter_words.split()]

    for vacancy in vacancies_list:
        title = vacancy.title.lower()
        if any(word in title for word in words_list):
            result.append(vacancy)

    return result


def get_vacancies_by_salary(filtered_vacancies: list[Vacancy], salary_range: str) -> list[Vacancy]:
    """Фильтрует вакансии по зп"""
    if not filtered_vacancies or not salary_range:
        return []

    result = []

    try:
        u_salary_from, u_salary_to = map(int, salary_range.split(" - "))
    except (ValueError, AttributeError):
        return filtered_vacancies

    for vacancy in filtered_vacancies:
        # print(vacancy)
        if vacancy.salary_from == "0" and vacancy.salary_to == "0":
            continue

        if int(vacancy.salary_from) < int(vacancy.salary_to):
            if u_salary_from == 0 and u_salary_to == 0:
                return filtered_vacancies
            elif u_salary_to == 0 and u_salary_from <= int(vacancy.salary_from):
                result.append(vacancy)
            elif u_salary_from == 0 and u_salary_to >= int(vacancy.salary_to):
                result.append(vacancy)
            elif u_salary_from <= int(vacancy.salary_from) and u_salary_to >= int(vacancy.salary_to):
                result.append(vacancy)

        elif int(vacancy.salary_to) < int(vacancy.salary_from):
            print(
                f"Обнаружена ошибка: перепутан зарплатный диапазон "
                f"{vacancy.salary_to} - {vacancy.salary_from} "
                f"в вакансии: {vacancy}"
            )
            # вызывают ошибку в тесте
            vacancy.salary_from = vacancy.salary_to
            vacancy.salary_to = vacancy.salary_from

    return result


def sort_vacancies(ranged_vacancies: list[Vacancy], ascending: bool = True) -> list[Vacancy]:
    """Сортировка фильтрованных вакансий"""
    if not ranged_vacancies:
        return []

    def get_salary(vacancy):  # type: ignore[no-untyped-def]
        """Извлекает минимальную зарплату из строки"""
        salary_from = int(vacancy.salary_from) if vacancy.salary_from else 0
        salary_to = int(vacancy.salary_to) if vacancy.salary_to else 0
        if salary_from > 0 or salary_to > 0:
            return min(salary_from, salary_to or float("inf"))
        return 0

    return sorted(ranged_vacancies, key=get_salary, reverse=not ascending)


def get_top_vacancies(sorted_vacancies: list[Vacancy], top_n: int) -> list[Vacancy]:
    """Получение топа вакансий в заданном количестве"""
    if not sorted_vacancies or top_n <= 0:
        return []

    return sorted_vacancies[:top_n]


def print_vacancies(top_vacancies):  # type: ignore[no-untyped-def]
    """Вывод желаемого количества вакансий в человекочитаемом виде"""
    if not top_vacancies:
        print("Нет вакансий для отображения.")
        return

    for vacancy in top_vacancies:
        if vacancy.salary_from != "0" and vacancy.salary_to != "0":
            print(f"Вакансия: {vacancy.title}")
            print(f"Зарплата: {vacancy.salary_from}")
            print(f"Зарплата: {vacancy.salary_to}")
            print(f"URL: {vacancy.url}")
        elif vacancy.salary_from != "0" and vacancy.salary_to == "0":
            print(f"Вакансия: {vacancy.title}")
            print(f"Зарплата: {vacancy.salary_from}")
            print(f"URL: {vacancy.url}")
        elif vacancy.salary_from == "0" and vacancy.salary_to != "0":
            print(f"Вакансия: {vacancy.title}")
            print(f"Зарплата: {vacancy.salary_to}")
            print(f"URL: {vacancy.url}")
        # Обрезаем длинный текст
        req = vacancy.requirement if hasattr(vacancy, "requirement") else "Не указаны"
        if len(req) > 150:
            req = req[:150] + "..."
        print(f"Требования: {req}")

        resp = vacancy.responsibility if hasattr(vacancy, "responsibility") else "Не указаны"
        if len(resp) > 150:
            resp = resp[:150] + "..."
        print(f"Обязанности: {resp}")

        print("=" * 40)
