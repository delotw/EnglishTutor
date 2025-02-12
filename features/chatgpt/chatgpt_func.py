import httpx
from loguru import logger
from openai import AsyncOpenAI, APITimeoutError
from dotenv import load_dotenv
import os

from settings import CONTEXT_37, CONTEXT_38
load_dotenv()

API = os.getenv('CHATGPT')
PROXY = os.getenv('PROXY')

client = AsyncOpenAI(api_key=API,
                     http_client=httpx.AsyncClient(
                         proxy=PROXY,
                         transport=httpx.HTTPTransport(local_address="0.0.0.0"))
                     )


# Функция для получения контекста-методички, чтобы gpt мог оценивать письма
def get_context(path: str):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as err:
        print(f'Не получилось получить файл из-за {err}')


# Функция получения ответа от GPT для 37 задания
async def get_score_37(mail_text: str, info_from_photo: str):
    logger.info('Отправлен запрос к ChatGPT')
    context = get_context(CONTEXT_37)

    try:
        response = await client.chat.completions.create(
            model='o1-mini',
            messages=[
                {
                    "role": "user",
                    "content": context
                },
                {
                    "role": "user",
                    "content": "Так, твой ответ должен содержать выдержанную оценку письма/эссе пользователя, основанную на критериях которые я тебе отправил. Выдели каждый критерий, балл за него и где есть недочеты, но как их исправлять не уточняй. В конце приведи сумму баллов за каждый критерий и итоговый балл. Не лей воду в комментарии к каждому ответу, твой комментарий должен быть кратким, но емким и с указанием на ошибки. Не делай это в виде таблички, а просто текстов опиши каждый критерий по пунктам."
                },
                {
                    "role": "assistant",
                    "content": "Хорошо, я готов оценивать письма, согласно критериям, которые ты мне отправил. Я жду письмо. Я не буду использовать Markdown разметку в своих ответах."
                },
                {
                    "role": "user",
                    "content": info_from_photo
                },
                {
                    "role": "assistant",
                    "content": "Отлично, я получил данные на основе которых пользователь пишет свое списьмо. Теперь жду само письмо пользователя."
                },
                {
                    "role": "user",
                    "content": mail_text
                }
            ]
        )
        logger.success('Получен ответ от ChatGPT')
    except APITimeoutError as e:
        logger.error(f'Ответ от ChatGPT не получен: {e}')

    return response.choices[0].message.content


# Функция получения ответа от GPT для 38 задания
async def get_score_38(mail_text: str, info_from_photo: str):
    context = get_context(CONTEXT_38)
    logger.info('Отправлен запрос к ChatGPT')

    try:
        response = await client.chat.completions.create(
            model='o1-mini',
            messages=[
                {
                    "role": "user",
                    "content": context
                },
                {
                    "role": "user",
                    "content": "Так, твой ответ должен содержать выдержанную оценку письма/эссе пользователя, основанную на критериях которые я тебе отправил. Выдели каждый критерий, балл за него и где есть недочеты, но как их исправлять не уточняй. В конце приведи сумму баллов за каждый критерий и итоговый балл. Не лей воду в комментарии к каждому ответу, твой комментарий должен быть кратким, но емким и с указанием на ошибки. Не делай это в виде таблички, а просто текстов опиши каждый критерий по пунктам."
                },
                {
                    "role": "assistant",
                    "content": "Хорошо, я готов оценивать письмо согласно тем критериям, что ты мне отправил. Жду текстовужю инфографику, на основе которой пользователь будет писать свое эссе."
                },
                {
                    "role": "user",
                    "content": info_from_photo
                },
                {
                    "role": "assistant",
                    "content": "Отлично, я получил данные на основе которых пользователь пишет свое эссе. Теперь жду само письмо пользователя."
                },
                {
                    "role": "user",
                    "content": mail_text
                }

            ]
        )
    except APITimeoutError as e:
        logger.error(f'Не получен ответ от ChatGPT: {e}')

    return response.choices[0].message.content
