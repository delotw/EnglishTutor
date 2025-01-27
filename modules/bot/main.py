from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
