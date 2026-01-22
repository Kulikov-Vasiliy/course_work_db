class Vacancy:
    """Класс для обработки вакансиями"""

    def __init__(
        self,
        title: str,
        url: str,
        salary_from: str,
        salary_to: str,
        currency: str | None,
        requirement: str = "Требования не указаны",
        responsibility: str = "Обязанности не указаны",
    ) -> None:
        self.title = title
        self.url = url
        self.salary_from = salary_from if salary_from else "0"
        self.salary_to = salary_to if salary_to else "0"
        self.currency = currency
        self.requirement = requirement
        self.responsibility = responsibility

    @staticmethod
    def cast_to_object_list(wanted: list[dict]) -> list:
        vacancies_list = []
        for item in wanted:
            if item:
                # print(item)
                title = item.get("title")
                url = item.get("alternate_url")
                from_salary = item.get("salary_from") if item.get("salary_from") is not None else "0"
                to_salary = item.get("salary_to") if item.get("salary_to") is not None else "0"
                currency = item.get("currency", "")
                salary_from_str = str(f"{from_salary}")
                salary_to_str = str(f"{to_salary}")

                requirement = item.get("requirement", "Требования не указаны")
                responsibility = item.get("responsibility", "Обязанности не указаны")
                vacancies_list.append(
                    Vacancy(
                        title,  # type: ignore[arg-type]
                        url,  # type: ignore[arg-type]
                        salary_from_str,
                        salary_to_str,
                        currency,
                        requirement,
                        responsibility
                    )
                )

            if not item:
                return []
        return vacancies_list

    @property
    def salary_avg(self) -> int:
        """Вычисляет среднюю зарплату для сравнения."""
        if int(self.salary_from) > 0 and int(self.salary_to) > 0:
            return int((int(self.salary_from) + int(self.salary_to)) / 2)
        elif int(self.salary_from) > 0:
            return int(self.salary_from)
        elif int(self.salary_to) > 0:
            return int(self.salary_to)
        else:
            return 0

    def __eq__(self, other: object) -> bool:
        """Определяет поведение оператора == (равенство)"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        # Считаем вакансии равными, если у них одинаковая средняя зарплата
        return self.salary_avg == other.salary_avg

    def __lt__(self, other: object) -> bool:
        """Определяет поведение оператора < (меньше чем)"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        # Сравниваем по средней зарплате
        # Важно: Сравнение зарплат в разной валюте (currency) тут не учитывается,
        # что может быть упрощением, но для примера сойдет.
        return self.salary_avg < other.salary_avg

    def __gt__(self, other: object) -> bool:
        """Определяет поведение оператора > (больше чем)"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        # Можно определить через __lt__ или напрямую
        return self.salary_avg > other.salary_avg

    def __repr__(self):  # type: ignore[no-untyped-def]
        """Дебаг-вывод в человекочитаемом формате"""
        if self.salary_from != "0" and self.salary_to != "0":
            return (
                f"Vacancy(title='{self.title}', url='{self.url}', salary='{self.salary_from} - "
                f"{self.salary_to} {self.currency}', "
                f"requirement={self.requirement[:]}, responsibility={self.responsibility[:]})"
            )
        elif self.salary_from != "0" and self.salary_to == "0":
            return (
                f"Vacancy(title='{self.title}', url='{self.url}', salary='{self.salary_from} "
                f"{self.currency}', requirement={self.requirement[:]}, "
                f"responsibility={self.responsibility[:]})"
            )
        elif self.salary_from == "0" and self.salary_to != "0":
            return (
                f"Vacancy(title='{self.title}', url='{self.url}', salary='{self.salary_to} "
                f"{self.currency}', requirement={self.requirement[:]}, "
                f"responsibility={self.responsibility[:]})"
            )
        elif self.salary_from == "0" and self.salary_to == "0":
            return (
                f"Vacancy(title='{self.title}', url='{self.url}', salary='0', "
                f"requirement={self.requirement[:]}, responsibility={self.responsibility[:]})"
            )

    def __str__(self):  # type: ignore[no-untyped-def]
        """Вывод в человекочитаемом формате"""
        if self.salary_from != "0" and self.salary_to != "0":
            return (
                f"Вакансия: {self.title}\nЗарплата: {self.salary_from} - "
                f"{self.salary_to} {self.currency}\nURL: {self.url}\n"
                f"Требования: {self.requirement[:]}\nОбязанности: {self.responsibility[:]}\n" + "=" * 40
            )
        elif self.salary_from != "0" and self.salary_to == "0":
            return (
                f"Вакансия: {self.title}\nЗарплата: {self.salary_from} {self.currency}\nURL: {self.url}\n"
                f"Требования: {self.requirement[:]}\nОбязанности: {self.responsibility[:]}\n" + "=" * 40
            )
        elif self.salary_from == "0" and self.salary_to != "0":
            return (
                f"Вакансия: {self.title}\nЗарплата: {self.salary_to} {self.currency}\nURL: {self.url}\n"
                f"Требования: {self.requirement[:]}\nОбязанности: {self.responsibility[:]}\n" + "=" * 40
            )
        elif self.salary_from == "0" and self.salary_to == "0":
            return (
                f"Вакансия: {self.title}\nЗарплата: 0\nURL: {self.url}\n"
                f"Требования: {self.requirement[:]}\nОбязанности: {self.responsibility[:]}\n" + "=" * 40
            )
