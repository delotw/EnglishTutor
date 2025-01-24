from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# получить простую inline-клавиатуру
async def get_inline(
    *,
    btns: dict[str, str],
        sizes: tuple[int] = (1,)):

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():

        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


# получить url-клавиатуру
async def get_inline_url(
    *,
    btns: dict[str, str],
        sizes: tuple[int] = (1,)):

    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():

        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()


# микс callback и url кнопок
async def get_mixed(
    *,
    btns: dict[str, str],
        sizes: tuple[int] = (1,)):

    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()
