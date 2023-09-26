import json

from src.dbmanager import DBManager
from src.hh import HeadHunter

hh = HeadHunter()
hh.get_employers()
hh.get_vacancies_count()
hh.get_vacancies()
hh_data = hh.get_format_and_search_vacancies()

db = DBManager()
db.fill_tables_from_files(hh_data)
db.get_companies_and_vacancies_count()
db.get_all_vacancies()
db.get_avg_salary()
db.get_vacancies_with_higher_salary()
db.get_vacancies_with_keyword()
