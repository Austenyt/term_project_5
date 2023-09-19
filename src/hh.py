from abc import ABC, abstractmethod
import requests


class API_abstract(ABC):
    """
    Абстрактный базовый класс API, который определяет метод `get_vacancies` для получения списка вакансий.
    """

    @abstractmethod
    def get_vacancies(self) -> None:
        pass


class HeadHunter(API_abstract):
    """
    Класс для работы с API HeadHunter. Наследует от абстрактного базового класса API_abstract.
    """

    def __init__(self) -> None:
        """
        Инициализация класса с заданием базового URL-адреса API HeadHunter.
        """

        self.url = "https://api.hh.ru/vacancies/"

    def get_vacancies(self, keyword='python') -> None:
        """
        Инициализация класса с заданием базового URL-адреса API HeadHunter.
        """

        params = {
            'text': f"NAME:{keyword}",  # Текст фильтра. В имени должно быть слово "Python"
            'area': 1,  # Поиск оcуществляется по вакансиям города Москва
            'page': 0,  # Индекс страницы поиска на HH
            'per_page': '100'  # Кол-во вакансий на 1 странице

        }
        response = requests.get(self.url, params)
        self.vacancies = response.json()['items']

    def get_format_and_search_vacancies(self):
        """
        Форматирование и поиск информации о вакансиях и работодателях на основе данных из self.vacancies.

        Returns:
            list: список словарей, содержащих информацию о работодателях и их вакансиях.
        """

        hh_emp_data = []
        seen_employers = set()  # Множество для отслеживания уже добавленных работодателей

        for vacancy in self.vacancies[:11]:
            employer_info = vacancy.get('employer', {})
            employer_id = employer_info.get('id')
            if employer_id not in seen_employers:
                salary_info = vacancy.get('salary', {})
                vacancy_salary = salary_info.get('from', 'Не указано') if salary_info else 'Не указано'
                emp_info = {
                    'employer_name': employer_info.get('name', 'Не указано'),
                    'employer_id': employer_id,
                    'vacancy_name': vacancy.get('name', 'Не указано'),
                    'vacancy_id': vacancy.get('id', 'Не указано'),
                    'vacancy_salary': vacancy_salary,
                    'vacancy_link': vacancy.get('alternate_url', 'Не указано'),
                }
                hh_emp_data.append(emp_info)
                seen_employers.add(employer_id)

        return hh_emp_data
