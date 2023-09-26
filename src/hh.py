import json
from abc import ABC, abstractmethod
from typing import List, Any

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

        self.employers = None
        self.url = "https://api.hh.ru/vacancies/"

    def get_employers(self, keyword='python') -> list[Any]:
        """
        Инициализация класса с заданием базового URL-адреса API HeadHunter.
        """
        self.employers = []

        for page in range(10):
            params = {
                'text': f"NAME:{keyword}",  # Текст фильтра. В имени должно быть слово "Python"
                'area': 1,  # Поиск оcуществляется по вакансиям города Москва
                'page': page,  # Индекс страницы поиска на HH
                'per_page': '100'  # Кол-во вакансий на 1 странице
            }
            response = requests.get(self.url, params)
            self.employers.extend(response.json()['items'])

        return self.employers

    def get_vacancies_count(self):
        """
        Считает количество вакансий для каждого работодателя и получает список первых 10 работодателей, у которых
        есть как минимум 2 вакансии. Возвращает список идентификаторов (id) первых десяти таких работодателей.
        """

        vacancies_list = {}

        for vacancy in self.employers:
            employer_id = vacancy['employer']['id']
            if employer_id not in vacancies_list:
                vacancies_list[employer_id] = 1
            else:
                vacancies_list[employer_id] += 1

        self.vacancies_count = {employer_id: count for employer_id, count in vacancies_list.items() if count >=2}
        # Получаем первые 10 id работодателей из self.vacancies_count.
        employers_ten = list(self.vacancies_count.keys())[:10]

        # Возвращаем список первых десяти id работодателей.
        return employers_ten
        # print(json.dumps(employers_ten, indent=4, ensure_ascii=False))

    def get_vacancies(self) -> None:

        """
        Получает вакансии первых 10 работодателей, у которых есть как минимум 2 вакансии. Извлекает из
        ответа сервера необходимую информацию о вакансиях и добавляет их в список self.vacancies.
        """

        employers_ten = self.get_vacancies_count()
        self.vacancies = []

        for employer_id in employers_ten:
            params = {
                'employer_id': employer_id,
                'area': 1,  # Поиск осуществляется по вакансиям города Москва
                'per_page': '100'  # Кол-во вакансий на 1 странице
            }
            response = requests.get(self.url, params)

            # Добавляем в список вакансии текущего работодателя
            self.vacancies.extend(response.json()['items'])

        # Возвращаем всю информацию о найденных вакансиях
        return self.vacancies
        # print(json.dumps(self.vacancies, indent=4, ensure_ascii=False))

    def get_format_and_search_vacancies(self):

        """
        Проходит по всем найденным вакансиям и сохраняет их информацию (employer_id, employer_name, employer_url,
        vacancy_name, vacancy_url, created_at) в форматированный список словарей. Возвращает этот список.
        """

        hh_emp_data = []

        for vacancy in self.vacancies:
            employer_name = vacancy['employer']['name']
            employer_id = vacancy['employer']['id']
            vacancy_name = vacancy['name']
            vacancy_id = vacancy['id']
            salary_info = vacancy.get('salary', {})
            vacancy_salary = salary_info.get('from', 'Не указано') if salary_info else 'Не указано'
            vacancy_link = vacancy['alternate_url']


            hh_emp_data.append({
                'employer_name': employer_name,
                'employer_id': employer_id,
                'vacancy_name': vacancy_name,
                'vacancy_id': vacancy_id,
                'vacancy_salary': vacancy_salary,
                'vacancy_link': vacancy_link
            })

        return hh_emp_data
        # print(json.dumps(hh_emp_data, indent=4, ensure_ascii=False))

        # """
        # Форматирование и поиск информации о вакансиях и работодателях на основе данных из self.vacancies.
        #
        # Returns:
        #     list: список словарей, содержащих информацию о работодателях и их вакансиях.
        # """
        #
        # hh_emp_data = []
        #
        #
        # for vacancy in self.vacancies:
        #     employer_info = vacancy.get('employer', {})
        #     employer_id = employer_info.get('id')
        #
        #
        #         salary_info = vacancy.get('salary', {})
        #         vacancy_salary = salary_info.get('from', 'Не указано') if salary_info else 'Не указано'
        #         emp_info = {
        #             'employer_name': employer_info.get('name', 'Не указано'),
        #             'employer_id': employer_id,
        #             'vacancy_name': vacancy.get('name', 'Не указано'),
        #             'vacancy_id': vacancy.get('id', 'Не указано'),
        #             'vacancy_salary': vacancy_salary,
        #             'vacancy_link': vacancy.get('alternate_url', 'Не указано'),
        #         }
        #         hh_emp_data.append(emp_info)
        #
        # print(json.dumps(hh_emp_data, indent=4, ensure_ascii=False))
