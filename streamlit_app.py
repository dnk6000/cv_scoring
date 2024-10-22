import os

import openai
import streamlit as st
import httpx

from parse_hh import get_candidate_info, get_job_description

# OPENAI_API_KEY = os.getenv(st.secrets["OPENAI_API_KEY"])
# OPENAI_PROXY = os.getenv(st.secrets["OPENAI_PROXY"])
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENAI_PROXY = st.secrets["OPENAI_PROXY"]

client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_PROXY is None or OPENAI_PROXY == "" \
                 else openai.OpenAI(api_key=OPENAI_API_KEY, http_client=httpx.Client(proxy=OPENAI_PROXY))


SYSTEM_PROMPT = """
Проскорь кандидата, насколько он подходит для данной вакансии.

Сначала напиши короткий анализ, который будет пояснять оценку.
Отдельно оцени качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и каким образом их решал?). Эта оценка должна учитываться при выставлении финальной оценки - нам важно нанимать таких кандидатов, которые могут рассказать про свою работу
Потом представь результат в виде оценки от 1 до 10.
""".strip()


def request_gpt(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1000,
        temperature=0,
    )
    return response.choices[0].message.content


st.title("CV Scoring App")

job_description_url = st.text_area("Enter the job description url")

cv_url = st.text_area("Enter the CV url")

if st.button("Score CV"):
    with st.spinner("Scoring CV..."):

        job_description = get_job_description(job_description_url)
        cv = get_candidate_info(cv_url)

        st.write("Job description:")
        st.write(job_description)
        st.write("CV:")
        st.write(cv)

        user_prompt = f"# ВАКАНСИЯ\n{job_description}\n\n# РЕЗЮМЕ\n{cv}"
        response = request_gpt(SYSTEM_PROMPT, user_prompt)

    st.write(response)