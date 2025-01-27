import httpx
from loguru import logger
from openai import AsyncOpenAI, APITimeoutError
from dotenv import load_dotenv
from features.mistral.mistral_func import get_info_from_photo
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
async def get_score_37(mail_text: str):
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
                    "role": "assistant",
                    "content": "Хорошо, я готов оценивать письма, согласно критериям, которые ты мне отправил. Я жду письмо. Я не буду использовать Markdown разметку в своих ответах."
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
async def get_score_38(mail_text: str, photo_url: str):
    desc = await get_info_from_photo(photo_url=photo_url)
    context = context = get_context(CONTEXT_38)

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
                    "role": "assistant",
                    "content": "Хорошо, я готов оценивать письмо согласно тем критериям, что ты мне отправил. Жду текстовужю инфографику, на основе которой пользователь будет писать свое эссе."
                },
                {
                    "role": "user",
                    "content": desc
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
