from src.vacancy import Vacancy


class TestVacancy:

    def test_init_defaults(self):
        """Проверка инициализации с дефолтными значениями"""
        v = Vacancy("Title", "http://url.com", "0", "0", None)
        assert v.title == "Title"
        assert v.url == "http://url.com"
        assert v.salary_from == "0"
        assert v.salary_to == "0"
        assert v.currency is None
        assert v.requirement == "Требования не указаны"
        assert v.responsibility == "Обязанности не указаны"

    def test_salary_avg_from_only(self):
        """Проверка расчета средней зарплаты, когда указана только нижняя граница"""
        v = Vacancy("T", "U", "50000", "0", "RUR")
        assert v.salary_avg == 50000

    def test_salary_avg_to_only(self):
        """Проверка расчета средней зарплаты, когда указана только верхняя граница"""
        v = Vacancy("T", "U", "0", "70000", "RUR")
        assert v.salary_avg == 70000

    def test_salary_avg_range(self):
        """Проверка расчета средней зарплаты, когда указан диапазон"""
        v = Vacancy("T", "U", "50000", "100000", "RUR")
        assert v.salary_avg == 75000

    def test_salary_avg_zero(self):
        """Проверка расчета средней зарплаты, когда зарплата не указана"""
        v = Vacancy("T", "U", "0", "0", None)
        assert v.salary_avg == 0

    def test_comparison_equal(self):
        """Проверка оператора равенства (==)"""
        v1 = Vacancy("A", "U1", "50000", "70000", "RUR")  # avg 60000
        v2 = Vacancy("B", "U2", "60000", "60000", "RUR")  # avg 60000
        assert (v1 == v2) is True

    def test_comparison_less_than(self):
        """Проверка оператора 'меньше чем' (<)"""
        v1 = Vacancy("A", "U1", "40000", "0", "RUR")  # avg 40000
        v2 = Vacancy("B", "U2", "0", "80000", "RUR")  # avg 80000
        assert (v1 < v2) is True
        assert (v2 < v1) is False

    def test_comparison_greater_than(self):
        """Проверка оператора 'больше чем' (>)"""
        v1 = Vacancy("A", "U1", "100000", "0", "RUR")  # avg 100000
        v2 = Vacancy("B", "U2", "0", "50000", "RUR")  # avg 50000
        assert (v1 > v2) is True
        assert (v2 > v1) is False

    def test_cast_to_object_list_valid_data(self):
        """Тестирование статического метода cast_to_object_list с корректными данными"""
        data = [
            {
                "title": "DevOps",
                "alternate_url": "http://url1.com",
                "salary_from": 100000,
                "salary_to": 150000,
                "currency": "RUR",
                "requirement": "Linux",
                "responsibility": "CI/CD",
            },
            {
                "title": "Analyst",
                "alternate_url": "http://url2.com",
                "salary_from": None,
                "salary_to": 80000,
                "currency": "RUR",
            },
        ]
        vacancies = Vacancy.cast_to_object_list(data)
        assert len(vacancies) == 2
        assert isinstance(vacancies[0], Vacancy)
        assert vacancies[0].title == "DevOps"
        assert vacancies[1].salary_from == "0"
        assert vacancies[1].salary_to == "80000"

    def test_cast_to_object_list_empty_input(self):
        """Тестирование статического метода с пустым списком"""
        vacancies = Vacancy.cast_to_object_list([])
        assert len(vacancies) == 0

    def test_repr_method(self):
        """Тестирование метода __repr__ для отладочного вывода"""
        v = Vacancy("Manager", "http://url.com", "40000", "60000", "USD")
        expected_repr = ("Vacancy(title='Manager', url='http://url.com', salary='40000 - 60000 USD', "
                         "requirement=Требования не указаны, responsibility=Обязанности не указаны)")
        assert repr(v) == expected_repr

    def test_str_method_full_salary(self):
        """Тестирование метода __str__ для пользовательского вывода (полная ЗП)"""
        v = Vacancy("Coder", "http://code.com", "80000", "120000", "RUR")
        expected_str_start = ("Вакансия: Coder\nЗарплата: 80000 - 120000 RUR\n"
                              "URL: http://code.com\nТребования: Требования не указаны\n"
                              "Обязанности: Обязанности не указаны\n")
        assert v.__str__().startswith(expected_str_start)

    def test_str_method_no_salary(self):
        """Тестирование метода __str__ для пользовательского вывода (ЗП не указана)"""
        v = Vacancy("Intern", "http://int.com", "0", "0", None)
        expected_str_start = ("Вакансия: Intern\nЗарплата: 0\nURL: http://int.com\n"
                              "Требования: Требования не указаны\n"
                              "Обязанности: Обязанности не указаны\n")
        assert v.__str__().startswith(expected_str_start)
