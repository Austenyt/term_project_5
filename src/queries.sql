CREATE TABLE Employers (
    employer_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL
);

CREATE TABLE Vacancies (
    vacancy_id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    salary VARCHAR,
    vacancy_link TEXT,
    employer_id INTEGER REFERENCES Employers (employer_id)
);
