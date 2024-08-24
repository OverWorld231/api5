import requests
from itertools import count
from terminaltables import AsciiTable
import os
from dotenv import load_dotenv


def get_vacancies_headhunter(language="Python", page=0):
    url = "https://api.hh.ru/vacancies"
    area = 1
    period = 30
    params = {"area": area, "period": period, "text": language, "page": page}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def predict_rub_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        expected_salary = int((salary_to + salary_from) / 2)
    elif salary_from:
        expected_salary = int(salary_from * 0.8)
    elif salary_to:
        expected_salary = int(salary_to * 1.2)
    else:
        expected_salary = None
    return expected_salary


def get_headhunter_statistic():
    vacancies_by_language = {}
    languages = [
        "Python", "Jave", "Swift", "TypeScript", "Scala", "Shell", "Go", "С",
        "С#", "С++", "Ruby", "JavaScript"
    ]
    for language in languages:
        vacancies_processed = 0
        vacancy_salaries  = []
        for page in count(0):
            vacancies = get_vacancies_headhunter(language, page=page)
            if page >= vacancies['pages'] - 1:
                break
            for vacancy in vacancies["items"]:
                salary = vacancy.get("salary")
                if salary and salary["currency"] == "RUR":
                    predicted_salary = predict_rub_salary(
                        vacancy["salary"].get("from"),
                        vacancy["salary"].get("to"))
                    if predicted_salary:
                        vacancies_processed += 1
                        vacancy_salaries .append(predicted_salary)
        vacancies_found = vacancies["found"]
        if vacancy_salaries:
            average_salary = int(sum( vacancy_salaries ) / len(vacancy_salaries))
        else:
            continue
        vacancies_by_language[language] = {
                "vacancies_found": vacancies_found,
                "vacancies_processed": vacancies_processed,
                "average_salary": average_salary
            }
    return vacancies_by_language


def get_super_job_vacancies(token, language, page=0):
    url = "https://api.superjob.ru/2.0/vacancies/"
    period = 30
    params = {
        "keyword": language,
        "period": period,
        "town": "Москва",
        "page": page
    }
    headers = {"X-Api-App-Id": token}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def predict_rub_salary_for_superJob(token):
    vacancies_by_language = {}
    languages = [
        "Python", "Java", "Swift", "TypeScript", "Scala", "Shell", "Go", "С",
        "С#", "С++", "Ruby", "JavaScript"
    ]
    for language in languages:
        vacancies_processed = 0
        vacancy_salaries = []
        for page in count(0, 1):
            vacancies = get_super_job_vacancies(token, language, page=page)
            if not vacancies['objects']:
                break
            for vacancy in vacancies["objects"]:
                predicted_salary = predict_rub_salary(vacancy["payment_from"],
                                                    vacancy["payment_to"])
                if predicted_salary:
                    vacancies_processed += 1
                    vacancy_salaries.append(predicted_salary)
        total_vacancies = vacancies["total"]
        if vacancy_salaries:
            average_salary = int(sum(vacancy_salaries) / len(vacancy_salaries))
        else:
            continue
        vacancies_by_language[language] = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary
        }
    return vacancies_by_language


def get_table(statistic):
    table_data = [[
        'Язык программирования', 'Вакансий найдено', "Вакансий обработанно",
        "Средняя зарплата"
    ]]
    for language, vacancy in statistic.items():
        table_data.append([
            language, vacancy["vacancies_found"],
            vacancy["vacancies_processed"], vacancy["average_salary"]
        ])
    table = AsciiTable(table_data)
    return table.table


def main():
    load_dotenv()
    token = os.environ['SJ_KEY']
    print(get_table(predict_rub_salary_for_superJob(token)))
    print(get_table(get_headhunter_statistic()))


if __name__ == "__main__":
    main()
