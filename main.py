import requests
from itertools import count
from terminaltables import AsciiTable
import os
from dotenv import load_dotenv


def vacansies_headhunter(language="Python", page=0):
    url = "https://api.hh.ru/vacancies"
    params = {"area": 1, "period": 30, "text": language, "page": page}
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
    vacansies_by_language = {}
    languages = [
        "Python", "Jave", "Swift", "TypeScript", "Scala", "Shell", "Go", "С",
        "С#", "С++", "Ruby", "JavaScript"
    ]
    for language in languages:
        salary_vacansies = []
        for page in count(0):
            vacansies = vacansies_headhunter(language, page=page)
            if page >= vacansies['pages'] - 1:
                break
            for vacansy in vacansies["items"]:
                salary = vacansy.get("salary")
                if salary and salary["currency"] == "RUR":
                    predict_salary = predict_rub_salary(
                        vacansy["salary"].get("from"),
                        vacansy["salary"].get("to"))
                    if predict_salary:
                        salary_vacansies.append(predict_salary)
        if salary_vacansies:
            average_salary = int(sum(salary_vacansies) / len(salary_vacansies))
        vacansies_by_language[language] = {
            "vacancies_found": vacansies["found"],
            "vacancies_processed": len(salary_vacansies),
            "average_salary": average_salary
        }
    return vacansies_by_language


def super_job(token, language, page=0):
    url = "https://api.superjob.ru/2.0/vacancies/"
    params = {
        "keyword": language,
        "period": 30,
        "town": "Москва",
        "page": page
    }
    headers = {"X-Api-App-Id": token}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def predict_rub_salary_for_superJob(token):
    vacansies_by_language = {}
    languages = [
        "Python", "Java", "Swift", "TypeScript", "Scala", "Shell", "Go", "С",
        "С#", "С++", "Ruby", "JavaScript"
    ]
    for language in languages:
        salary_vacansies = []
        for page in count(0, 1):
            vacansies = super_job(token, language, page=page)
            if not vacansies['objects']:
                break
            for vacansy in vacansies["objects"]:
                predict_salary = predict_rub_salary(vacansy["payment_from"],
                                                    vacansy["payment_to"])
                if predict_salary:
                    salary_vacansies.append(predict_salary)
        if salary_vacansies:
            average_salary = int(sum(salary_vacansies) / len(salary_vacansies))
        vacansies_by_language[language] = {
            "vacancies_found": vacansies["total"],
            "vacancies_processed": len(salary_vacansies),
            "average_salary": average_salary
        }
    return vacansies_by_language


def tables(statistic):
    table_data = [[
        'Язык программирования', 'Вакансий найдено', "Вакансий обработанно",
        "Средняя зарплата"
    ]]
    for language, vacansie in statistic.items():
        table_data.append([
            language, vacansie["vacancies_found"],
            vacansie["vacancies_processed"], vacansie["average_salary"]
        ])
    table = AsciiTable(table_data)
    return table.table


def main():
    load_dotenv()
    token = os.environ['SJ_KEY']
    print(tables(predict_rub_salary_for_superJob(token)))
    print(tables(get_headhunter_statistic()))


if __name__ == "__main__":
    main()