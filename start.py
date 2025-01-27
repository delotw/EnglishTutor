from modules.handlers.user_handlers import user_router
from modules.handlers.admin_handlers import admin_router
from settings import ALLOWED_UPDATES, EXPERTS
from common.commands_list import private
import asyncio
from loguru import logger
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv
load_dotenv()


logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | {level} | <cyan>{message}</cyan>",
    level="INFO",
    enqueue=True,
    colorize=True
)

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
bot.my_admins_list = EXPERTS

dp = Dispatcher()
dp.include_routers(user_router, admin_router)


async def main():
    try:
        logger.success('Бот был запущен!')
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
        await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)
    except KeyboardInterrupt:
        logger.info('Бот был включен')


if __name__ == "__main__":
    asyncio.run(main())
