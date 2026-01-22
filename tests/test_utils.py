from unittest.mock import patch

from src.utils import filter_vacancies, get_top_vacancies, get_vacancies_by_salary, print_vacancies, sort_vacancies


class TestFilterVacancies:

    def test_filter_with_match(self, sample_vacancies_list_objects):
        """Проверка фильтрации, когда слова совпадают"""
        filter_words = "Python Java"
        filtered = filter_vacancies(sample_vacancies_list_objects, filter_words)
        assert len(filtered) == 2
        titles = [v.title for v in filtered]
        assert "Python Developer (Mid)" in titles
        assert "Java Developer (Senior)" in titles

    def test_filter_no_match(self, sample_vacancies_list_objects):
        """Проверка фильтрации, когда совпадений нет"""
        filter_words = "C++"
        filtered = filter_vacancies(sample_vacancies_list_objects, filter_words)
        assert len(filtered) == 0

    def test_filter_case_insensitivity(self, sample_vacancies_list_objects):
        """Проверка, что фильтр не чувствителен к регистру"""
        filter_words = "qa"
        filtered = filter_vacancies(sample_vacancies_list_objects, filter_words)

        # Убеждаемся, что найдена ровно 1 вакансия
        assert len(filtered) == 1

        assert filtered[0].title == "QA Engineer (Junior)"

    def test_filter_empty_words(self, sample_vacancies_list_objects):
        """Проверка обработки пустой строки фильтра"""
        filtered = filter_vacancies(sample_vacancies_list_objects, "")
        assert len(filtered) == 0


class TestGetVacanciesBySalary:

    def test_filter_salary_range_match_full_range(self, sample_vacancies_list_objects):
        """Фильтрация по полному диапазону, который охватывает несколько вакансий"""
        salary_range = "100000 - 160000"
        filtered = get_vacancies_by_salary(sample_vacancies_list_objects, salary_range)

        # Ожидаем Python (100-150) и DevOps (130-160). Java (120-180) не попадает из-за верхней границы 180 > 160
        assert len(filtered) == 2
        titles = sorted([v.title for v in filtered])
        assert titles == ["DevOps Engineer (Lead)", "Python Developer (Mid)"]

    def test_filter_salary_range_match_from_only(self, sample_vacancies_list_objects):
        """Фильтрация по нижней границе диапазона пользователя (от 80k и выше)"""
        salary_range = "80000 - 0"  # u_salary_to == 0

        # ВАЖНО: Ваша функция get_vacancies_by_salary ожидает, что
        # у вакансий будут указаны ОБЕ границы зарплаты, чтобы они попали в этот фильтр.
        # Sales Manager (80k - 0) не попадет в filtered из-за особенности вашей логики if/elif.

        filtered = get_vacancies_by_salary(sample_vacancies_list_objects, salary_range)

        # Ожидаемые вакансии, которые проходят фильтр вашей функции:
        # Python Developer (100k - 150k) -> средняя 125k
        # Java Developer (120k - 180k) -> средняя 150k
        # DevOps Engineer (130k - 160k) -> средняя 145k

        # Sales Manager (80k - 0) отсекается, так как у него to="0"

        assert len(filtered) == 3

        # Извлекаем заголовки из списка объектов Vacancy
        actual_titles = sorted([v.title for v in filtered])

        expected_titles = sorted(["DevOps Engineer (Lead)", "Java Developer (Senior)", "Python Developer (Mid)"])

        # Сравниваем полученный список заголовков с ожидаемым списком
        assert actual_titles == expected_titles

    def test_filter_salary_range_match_to_only(self, sample_vacancies_list_objects):
        """Фильтрация по верхней границе диапазона пользователя"""
        salary_range = "0 - 40000"  # u_salary_from == 0

        # Ожидаем Cleaner (0k-40k), т.к. 40k >= 40k.
        filtered = get_vacancies_by_salary(sample_vacancies_list_objects, salary_range)

        assert len(filtered) == 1
        assert filtered[0].title == "Cleaner"

    def test_filter_salary_range_no_match(self, sample_vacancies_list_objects):
        """Фильтрация по диапазону, которому ни одна вакансия не соответствует"""
        salary_range = "200000 - 300000"
        filtered = get_vacancies_by_salary(sample_vacancies_list_objects, salary_range)
        assert len(filtered) == 0

    def test_filter_salary_invalid_input(self, sample_vacancies_list_objects):
        """Обработка некорректного формата строки зарплаты - должен вернуть исходный список"""
        salary_range = "abc - def"
        filtered = get_vacancies_by_salary(sample_vacancies_list_objects, salary_range)
        assert len(filtered) == len(sample_vacancies_list_objects)

    def test_filter_salary_zero_ranges(self, sample_vacancies_list_objects):
        """
        Проверка поведения при нулевых диапазонах (ввод пользователя 0-0).
        Функция возвращает исходный список.
        """
        salary_range = "0 - 0"
        filtered = get_vacancies_by_salary(sample_vacancies_list_objects, salary_range)
        assert len(filtered) == len(sample_vacancies_list_objects)


class TestSortVacancies:

    def test_sort_ascending(self, sample_vacancies_list_objects):
        """Сортировка по возрастанию минимальной зарплаты"""
        sorted_list = sort_vacancies(sample_vacancies_list_objects, ascending=True)
        # Ожидаемый порядок по минимальной ЗП: Junior (0),
        # Cleaner (0, min is 0), QA (50k), Sales (80k),
        # Python (100k), Java (120k), DevOps (130k)
        assert sorted_list[0].title == "Junior Intern"
        assert sorted_list[1].title == "Cleaner"
        assert (sorted_list[-1].title ==
                "DevOps Engineer (Lead)")

    def test_sort_descending(self, sample_vacancies_list_objects):
        """Сортировка по убыванию минимальной зарплаты"""
        sorted_list = sort_vacancies(sample_vacancies_list_objects, ascending=False)
        # Обратный порядок
        assert sorted_list[0].title == "DevOps Engineer (Lead)"
        assert sorted_list[-1].title == "Cleaner"

    def test_get_top_n_normal(self, sample_vacancies_list_objects):
        """Получение заданного количества (N=3) top-вакансий"""
        top_n = 3
        top_list = get_top_vacancies(sample_vacancies_list_objects, top_n)

        assert len(top_list) == top_n

        # Проверяем, что вернулись первые N элементов из исходного списка
        assert top_list[0].title == 'Python Developer (Mid)'
        assert top_list[1].title == 'Java Developer (Senior)'
        assert top_list[2].title == 'QA Engineer (Junior)'

    def test_get_top_n_more_than_available(self, sample_vacancies_list_objects):
        """Запрос N больше, чем всего вакансий (N=100 при 5 вакансиях)"""
        top_n = 100
        top_list = get_top_vacancies(sample_vacancies_list_objects, top_n)

        # Ожидаем получить все доступные 5 вакансий
        assert len(top_list) == 7
        assert top_list[-1].title == 'Cleaner'

    def test_get_top_n_zero(self, sample_vacancies_list_objects):
        """Запрос N=0 должен вернуть пустой список"""
        top_n = 0
        top_list = get_top_vacancies(sample_vacancies_list_objects, top_n)

        assert len(top_list) == 0
        assert top_list == []

    def test_get_top_n_negative(self, sample_vacancies_list_objects):
        """Запрос отрицательного N должен вернуть пустой список"""
        top_n = -1
        top_list = get_top_vacancies(sample_vacancies_list_objects, top_n)

        assert len(top_list) == 0
        assert top_list == []

    def test_get_top_n_empty_input(self):
        """Передача пустого списка вакансий должна вернуть пустой список"""
        sorted_vacancies = []
        top_n = 5
        top_list = get_top_vacancies(sorted_vacancies, top_n)

        assert len(top_list) == 0
        assert top_list == []


class TestPrintVacancies:
    """Тестирование функции вывода требует перехвата стандартного вывода (stdout)"""

    @patch("sys.stdout")
    def test_print_vacancies_output_format(self, mock_stdout, sample_vacancies_list_objects):
        """Проверка, что функция печати вызывает print с ожидаемым форматом"""
        # Берем одну вакансию для простоты проверки: Python Developer (100k-150k)
        vacancy_to_print = sample_vacancies_list_objects[0]
        print_vacancies([vacancy_to_print])

        # Convert the calls to a single string for easier assertion, simulating the output
        # Используем mock_stdout.write для захвата при использовании print() в Python 3+
        output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)

        assert "Вакансия: Python Developer (Mid)" in output
        assert "Зарплата: 100000" in output
        assert "Зарплата: 150000" in output
        assert "URL: url1" in output
        assert "=" * 40 in output

    @patch("sys.stdout")
    def test_print_vacancies_empty_list(self, mock_stdout):
        """Проверка вывода при пустом списке вакансий"""
        print_vacancies([])
        output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
        assert "Нет вакансий для отображения." in output
