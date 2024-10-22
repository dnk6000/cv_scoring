import requests


def get_html(url: str):
    return requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        },
    )


# print(response.text)
# with open("vacancy.html", "w") as f:
#     f.write(response.text)

from bs4 import BeautifulSoup


def extract_vacancy_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # Извлечение заголовка вакансии
    title = soup.find("h1", {"data-qa": "vacancy-title"}).text.strip()

    # Извлечение зарплаты
    salary = soup.find(
        "span", {"data-qa": "vacancy-salary-compensation-type-net"}
    ).text.strip()

    # Извлечение опыта работы
    experience = soup.find("span", {"data-qa": "vacancy-experience"}).text.strip()

    # Извлечение типа занятости и режима работы
    employment_mode = soup.find(
        "p", {"data-qa": "vacancy-view-employment-mode"}
    ).text.strip()

    # Извлечение компании
    company = soup.find("a", {"data-qa": "vacancy-company-name"}).text.strip()

    # Извлечение местоположения
    location = soup.find("p", {"data-qa": "vacancy-view-location"}).text.strip()

    # Извлечение описания вакансии
    description = soup.find("div", {"data-qa": "vacancy-description"}).text.strip()

    # Извлечение ключевых навыков
    skills = [
        skill.text.strip()
        for skill in soup.find_all(
            "div", {"class": "magritte-tag__label___YHV-o_3-0-13"}
        )
    ]

    # Формирование строки в формате Markdown
    markdown = f"""
# {title}

**Компания:** {company}
**Зарплата:** {salary}
**Опыт работы:** {experience}
**Тип занятости и режим работы:** {employment_mode}
**Местоположение:** {location}

## Описание вакансии
{description}

## Ключевые навыки
- {'\n- '.join(skills)}
"""

    return markdown.strip()


# from bs4 import BeautifulSoup

def extract_candidate_data_old(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Извлечение основных данных кандидата
    name = soup.find('h2', {'data-qa': 'bloko-header-1'}).text.strip()
    gender_age = soup.find('p').text.strip()
    location = soup.find('span', {'data-qa': 'resume-personal-address'}).text.strip()
    job_title = soup.find('span', {'data-qa': 'resume-block-title-position'}).text.strip()
    job_status = soup.find('span', {'data-qa': 'job-search-status'}).text.strip()

    # Извлечение опыта работы
    experience_section = soup.find('div', {'data-qa': 'resume-block-experience'})
    experience_items = experience_section.find_all('div', class_='resume-block-item-gap')
    experiences = []
    for item in experience_items:
        period = item.find('div', class_='bloko-column_s-2').text.strip()
        duration = item.find('div', class_='bloko-text').text.strip()
        period = period.replace(duration, f" ({duration})")

        company = item.find('div', class_='bloko-text_strong').text.strip()
        position = item.find('div', {'data-qa': 'resume-block-experience-position'}).text.strip()
        description = item.find('div', {'data-qa': 'resume-block-experience-description'}).text.strip()
        experiences.append(f"**{period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n")

    # Извлечение ключевых навыков
    skills_section = soup.find('div', {'data-qa': 'skills-table'})
    skills = [skill.text.strip() for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})]

    # Формирование строки в формате Markdown
    markdown = f"# {name}\n\n"
    markdown += f"**{gender_age}**\n\n"
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += f"**Должность:** {job_title}\n\n"
    markdown += f"**Статус:** {job_status}\n\n"
    markdown += "## Опыт работы\n\n"
    for exp in experiences:
        markdown += exp + "\n"
    markdown += "## Ключевые навыки\n\n"
    markdown += ', '.join(skills) + "\n"

    return markdown


def extract_candidate_data(html_content):
    # Инициализация BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Сбор информации о кандидате
    resume_data = {}

    # Имя кандидата
    try:
        resume_data['name'] = soup.find('h1', {'data-qa': 'resume-header-title'}).get_text(strip=True)
    except AttributeError:
        resume_data['name'] = 'Name not found'

    # Желаемая должность
    try:
        resume_data['desired_position'] = soup.find('span', {'data-qa': 'resume-block-title-position'}).get_text(
            strip=True)
    except AttributeError:
        resume_data['desired_position'] = 'Desired position not found'

    # Зарплата
    try:
        salary_section = soup.find('span', {'data-qa': 'resume-block-salary'}).find_all(string=True)
        resume_data['salary'] = ' '.join(part.strip() for part in salary_section if part.strip())
    except AttributeError:
        resume_data['salary'] = 'Salary not found'

    # Пол кандидата
    try:
        gender_section = soup.find('span', {'data-qa': 'resume-personal-gender'})
        resume_data['gender'] = gender_section.get_text(strip=True)
    except AttributeError:
        resume_data['gender'] = 'Gender not found'

    # Возраст кандидата
    try:
        age_section = soup.find('span', {'data-qa': 'resume-personal-age'}).find('span')
        age_text_parts = age_section.find_all(string=True)
        resume_data['age'] = ' '.join(part.strip() for part in age_text_parts if part.strip())
    except AttributeError:
        resume_data['age'] = 'Age not found'

    # Опыт работы
    experiences = []
    experience_sections = soup.find_all('div', {'class': 'resume-block-item-gap'})
    for section in experience_sections:
        company_name = section.find('div', {'class': 'bloko-text bloko-text_strong'}).get_text(
            strip=True) if section.find('div', {'class': 'bloko-text bloko-text_strong'}) else ''
        position = section.find('div', {'data-qa': 'resume-block-experience-position'}).get_text(
            strip=True) if section.find('div', {'data-qa': 'resume-block-experience-position'}) else ''
        description = section.find('div', {'data-qa': 'resume-block-experience-description'}).get_text(
            strip=True) if section.find('div', {'data-qa': 'resume-block-experience-description'}) else ''
        period = section.find('div', {
            'class': 'bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2'}).get_text(
            strip=True) if section.find('div', {
            'class': 'bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2'}) else ''
        experience_text = f"{period} {company_name} {position} {description}".strip()
        if experience_text:
            experiences.append(experience_text)

    # Образование
    educations = []
    education_sections = soup.find_all('div', {'data-qa': 'resume-block-education-item'})
    for section in education_sections:
        education_text = section.get_text(strip=True)
        if education_text and education_text not in educations:
            educations.append(education_text)

    # Навыки
    try:
        skills_section = soup.find('div', {'data-qa': 'resume-block-skills'})
        resume_data['skills'] = skills_section.get_text(strip=True)
    except AttributeError:
        resume_data['skills'] = 'Skills not found'

    # Контакты (зависит от доступности)
    try:
        contacts_section = soup.find('div', {'data-qa': 'resume-block-contacts'})
        resume_data['contacts'] = contacts_section.get_text(strip=True)
    except AttributeError:
        resume_data['contacts'] = 'Contacts not found'

    # Формирование строки в формате markdown
    markdown_output = f"""
# {resume_data['name']}

**Пол:** {resume_data['gender']}
**Возраст:** {resume_data['age']}
**Желаемая должность:** {resume_data['desired_position']}
**Ожидаемая зарплата:** {resume_data['salary']}

## Опыт работы:
"""
    for experience in experiences:
        markdown_output += f"- {experience}\n"

    markdown_output += "\n## Образование:\n"
    for education in educations:
        markdown_output += f"- {education}\n"

    markdown_output += f"""

## Навыки:
{resume_data['skills']}

## Контакты:
{resume_data['contacts']}
"""

    return markdown_output


def get_candidate_info(url: str):
    response = get_html(url)
    return extract_candidate_data(response.text)

def get_job_description(url: str):
    response = get_html(url)
    return extract_vacancy_data(response.text)

if __name__ == "__main__":
    url = "https://penza.hh.ru/vacancy/108341136?from=applicant_recommended&hhtmFrom=main"
    print(get_job_description(url))
    # url = "https://penza.hh.ru/resume/50ef2f9b0002e6e6a30039ed1f68556e504677"
    # print(get_candidate_info(url))
