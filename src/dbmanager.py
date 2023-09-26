import json
import psycopg2

class DBManager:
    def __init__(self):
        """
        Инициализация объекта менеджера базы данных.
        """
        self.conn = None

    def connect_to_db(self) -> None:
        """
        Подключение к базе данных. В случае ошибки, отображает сообщение об ошибке.
        """

        try:
            self.conn = psycopg2.connect(
                host="localhost",
                database="hh_job",
                user="postgres",
                password="2so1lTrf6JY-"
            )
        except psycopg2.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")

    def close_db_connection(self) -> None:
        """
        Закрытие соединения с базой данных и вывод сообщения об успешном закрытии.
        """

        if self.conn:
            self.conn.close()
            print("Соединение с базой данных закрыто")

    def fill_tables_from_files(self, hh_emp_data):
        """
        Создание и заполнение таблиц Employers и Vacancies данными из списка hh_emp_data. В случае ошибки, откатывает
        транзакцию и выводит сообщение об ошибке.

        Args:
            hh_emp_data (list): Список словарей с данными о работодателях и вакансиях.
        """

        self.connect_to_db()  # Подключение к базе данных

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS Employers (employer_id SERIAL PRIMARY KEY, employer_name VARCHAR('
                    '255))'
                )
                cur.execute(
                    'CREATE TABLE IF NOT EXISTS Vacancies (vacancy_id VARCHAR(255) PRIMARY KEY, '
                    'vacancy_name VARCHAR(255), vacancy_salary VARCHAR(255), '
                    'vacancy_link VARCHAR(255), employer_id INT REFERENCES Employers(employer_id) NOT NULL)'
                )

                # Очищаем таблицы перед вставкой новых данных
                cur.execute('DELETE FROM Vacancies')
                cur.execute('DELETE FROM Employers')

                for item in hh_emp_data:
                    # Вставляем данные в таблицу Employers
                    cur.execute(
                        'INSERT INTO Employers (employer_id, employer_name) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                        (item['employer_id'], item['employer_name'])
                    )

                    # Вставляем данные в таблицу Vacancies
                    cur.execute(
                        'INSERT INTO Vacancies (vacancy_id, vacancy_name, vacancy_salary, vacancy_link, employer_id) '
                        'VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING',
                        (item['vacancy_id'], item['vacancy_name'], item['vacancy_salary'], item['vacancy_link'],
                         item['employer_id'])
                    )

                self.conn.commit()
                print("Данные успешно добавлены в таблицы")
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении данных в таблицы: {e}")
            self.conn.rollback()
        finally:
            self.close_db_connection()  # Закрытие соединения с базой данных

    def get_companies_and_vacancies_count(self) -> None:
        """
        Получение списка компаний с количеством вакансий для каждой компании и отображение результатов.
        В случае ошибки, выводит сообщение об ошибке.
        """

        self.connect_to_db()  # Подключение к базе данных

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    'SELECT Employers.employer_name, COUNT(Vacancies.vacancy_id) AS vacancy_count '
                    'FROM Employers '
                    'LEFT JOIN Vacancies ON Employers.employer_id = Vacancies.employer_id '
                    'GROUP BY Employers.employer_name '
                    'ORDER BY Employers.employer_name'
                )
                comp_count = cur.fetchall()
                print(f"Список компаний и количество их вакансий: {json.dumps(comp_count, indent=4, ensure_ascii=False)}")
        except psycopg2.Error as e:
            print(f"Ошибка при получении данных: {e}")
        finally:
            self.close_db_connection()  # Закрытие соединения с базой данных

    def get_all_vacancies(self) -> None:

        """
        Получение всех вакансий и отображение результатов. В случае ошибки, выводит сообщение об ошибке.
        """

        self.connect_to_db()  # Подключение к базе данных
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    'SELECT Employers.employer_name, Vacancies.vacancy_name, Vacancies.vacancy_salary, Vacancies.vacancy_link '
                    'FROM Vacancies '
                    'LEFT JOIN Employers ON Vacancies.employer_id = Employers.employer_id'
                )
                all_vac = cur.fetchall()
                print(f"Список всех вакансий: {json.dumps(all_vac, indent=4, ensure_ascii=False)}")
        except psycopg2.Error as e:
            print(f"Ошибка при получении данных: {e}")
        finally:
            self.close_db_connection()  # Закрытие соединения с базой данных

    def get_avg_salary(self) -> float or None:
        """
        Получение средней зарплаты по вакансиям и отображение результата.
        В случае ошибки, выводит сообщение об ошибке.
        Возвращает среднюю зарплату в виде числа с плавающей точкой или None, если ее не удалось получить.
        """
        self.connect_to_db()  # Подключение к базе данных
        try:
            with self.conn.cursor() as cur:
                # Выполняем исправленный SQL-запрос с приведением типа
                cur.execute(
                    "SELECT AVG(CAST(vacancy_salary AS NUMERIC)) FROM vacancies WHERE vacancy_salary != 'Не указано'")

                # Получаем результат запроса
                avg_salary = cur.fetchone()

                # Выводим значение средней зарплаты (оно будет находиться в ячейке 0 кортежа)
                if avg_salary is not None:
                    self.avg_salary_float = float(avg_salary[0])
                    print(f"Средняя зарплата по вакансиям: {self.avg_salary_float:,.0f}")
                    return self.avg_salary_float
                else:
                    print("Не удалось получить среднюю зарплату.")
                    return None
        except psycopg2.Error as e:
            print(f"Ошибка при получении средней зарплаты: {e}")
            self.conn.rollback()
            return None
        finally:
            self.close_db_connection()  # Закрытие соединения с базой данных

    def get_vacancies_with_higher_salary(self) -> None:
        """
        Получение списка вакансий, у которых зарплата выше средней зарплаты и отображение результата. В случае ошибки,
        выводит сообщение об ошибке.
        """
        self.connect_to_db()
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT Employers.employer_name, Vacancies.vacancy_name, Vacancies.vacancy_salary, "
                    "Vacancies.vacancy_link "
                    "FROM Vacancies "
                    "LEFT JOIN Employers ON Vacancies.employer_id = Employers.employer_id "
                    "WHERE CAST(vacancies.vacancy_salary AS NUMERIC) > %s AND Vacancies.vacancy_salary != 'Не указано';",
                    (self.avg_salary_float,)
                )
                higher_salary_vacancies = cur.fetchall()
                print(f"Список вакансий с зарплатой выше средней: {json.dumps(higher_salary_vacancies, indent=4, ensure_ascii=False)}")
        except psycopg2.Error as e:
            print(f"Ошибка при получении вакансий с зарплатой выше средней зарплаты: {e}")
        finally:
            self.close_db_connection()

    def get_vacancies_with_keyword(self, keyword='Стажер') -> None:
        """
        Получение списка вакансий, содержащих указанное ключевое слово (по умолчанию "Стажер") и отображение результата.
        В случае ошибки, выводит сообщение об ошибке.

        Args:
            keyword (str, optional): Ключевое слово для поиска вакансий. По умолчанию 'Стажер'.
        """

        self.connect_to_db()
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM Vacancies WHERE vacancy_name LIKE '%{keyword}%';"
                )
                vacancies = cur.fetchall()
                print("Список вакансий, содержащих слово 'Стажер':")
                for vacancy in vacancies:
                    print(vacancy)
        except psycopg2.Error as e:
            print(f"Ошибка при получении данных из таблицы: {e}")
        finally:
            self.close_db_connection()

    def closs_conn(self) -> None:
        """
        Закрытие соединения с базой данных.
        """

        self.conn.close()