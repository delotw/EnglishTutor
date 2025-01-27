import asyncio
import os
from common.states_classes import Reg, CheckMail, CheckEssay, SolveTasksCategory
from features.chatgpt.chatgpt_func import get_score_37, get_score_38
from features.mistral.mistral_func import get_info_from_photo
from features.database.db_functions import *
from modules.keyboards.get_funcs.inline import *
from modules.keyboards.get_funcs.reply import *
from modules.bot.main import bot
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from loguru import logger


# Переменные
user_router = Router()
mark_down = ParseMode.MARKDOWN


@user_router.message(F.text == '/start')
async def send_welcome(message: Message):
    if await check_user_exists(uid=message.from_user.id):
        text = (f"<b>Привет, {await get_user_name(uid=message.from_user.id)} 👋</b> \nВыбери интересующий тебя раздел ниже:")
        kbd = await get_inline(
            btns={
                "Типовые задания 📋": "choose_tamplate_tasks",
                "Проверить письмо 📝": "choose_essay",
                "Профиль ℹ️": "profile",
                "Поддержка ☎️": "support",
            },
            sizes=(1, 1, 1,)
        )
        await message.answer(text=text, reply_markup=kbd)
    else:
        text = ('Привет 👋, меня зовут <b>Тьютор</b>! \nПропиши /reg для регистарции!')
        await message.answer(text=text)


# Регистрация пользователя в боте
@user_router.message(F.text == '/reg')
async def reg_first(message: Message, state: FSMContext):
    # Удаляем сообщение пользователя
    await message.delete()

    # Отправляем сообщение бота
    text = '1️⃣: Как тебя зовут?'
    bot_message = await message.answer(text=text)

    # Сохраняем ID сообщения бота
    await state.update_data(bot_message_id=bot_message.message_id)

    # Устанавливаем состояние
    await state.set_state(Reg.name)


@user_router.message(Reg.name)
async def reg_second(message: Message, state: FSMContext):
    # Удаляем сообщение пользователя
    await message.delete()

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    bot_message_id = data.get("bot_message_id")
    if bot_message_id:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=bot_message_id)

    # Сохраняем имя пользователя
    await state.update_data(name=message.text)

    # Отправляем новое сообщение
    text = f'2️⃣: {message.text}, в каком классе ты учишься?'
    kbd = await get_reply(
        'Прогуливаюсь мимо 🚶',
        '10',
        '11',
        sizes=(3,)
    )
    bot_message = await message.answer(text=text, reply_markup=kbd)

    # Сохраняем ID нового сообщения
    await state.update_data(bot_message_id=bot_message.message_id)

    # Устанавливаем следующее состояние
    await state.set_state(Reg.grade)


@user_router.message(Reg.grade)
async def reg_third(message: Message, state: FSMContext):
    # Удаляем сообщение пользователя
    await message.delete()

    # Удаляем предыдущее сообщение бота
    data = await state.get_data()
    bot_message_id = data.get("bot_message_id")
    if bot_message_id:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=bot_message_id)

    # Сохраняем класс
    await state.update_data(grade=message.text)

    # Отправляем новое сообщение
    text = '3️⃣: Как мне к тебе обращаться?'
    kbd = await get_reply(
        'Господин 🤵‍♂️',
        'Госпожа 🤵‍♀️',
        sizes=(2,)
    )
    bot_message = await message.answer(text=text, reply_markup=kbd)

    # Сохраняем ID нового сообщения
    await state.update_data(bot_message_id=bot_message.message_id)

    # Устанавливаем следующее состояние
    await state.set_state(Reg.sex)


@user_router.message(Reg.sex)
async def reg_final(message: Message, state: FSMContext):
    await message.delete()

    data = await state.get_data()
    bot_message_id = data.get("bot_message_id")
    if bot_message_id:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=bot_message_id)

    await state.update_data(sex=message.text)
    data = await state.get_data()
    uid = message.from_user.id
    name = str(data["name"])
    grade = data["grade"]
    sex = str(data["sex"])
    await create_user(uid=uid, name=name, grade=grade, sex=sex)

    text = ('🎉 <b>Регистрация успешно окончена, я рад, что мы познакомились поближе.</b> \n'
            'В качестве <b>подарка</b> тебе закинул немного баланса, чтобы ты мог протестировать нашу проверку писем нейронкой.\n'
            '----------')
    text_1 = "➡️ Нажми на кнопку ниже, чтобы перейти в главное меню!"
    kbd = await get_inline(
        btns={
            'В главное меню ✅': 'main_menu',
        },
        sizes=(1,)
    )

    bot_message_1 = await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await message.answer(text=text_1, reply_markup=kbd)
    await state.update_data(bot_message_ids=[bot_message_1.message_id])
    await asyncio.sleep(10)
    for message_id in [bot_message_1.message_id]:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        except Exception as e:
            print(f"Ошибка удаления сообщения: {e}")

    # Очищаем состояние
    await state.clear()


# * Основные хэндлеры для меню


@user_router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # сброс состояний пользователя
    text = (f"<b>Привет, {await get_user_name(uid=callback.from_user.id)} 👋</b> \nВыбери интересующий тебя раздел ниже:")
    kbd = await get_inline(
        btns={
            "Типовые задания 📋": "choose_tamplate_tasks",
            "Проверить письмо 📝": "choose_essay",
            "Профиль ℹ️": "profile",
            "Поддержка ☎️": "support",
        },
        sizes=(1, 1, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "profile")
async def menu_user_profile(callback: CallbackQuery):
    uid = callback.from_user.id
    user = await get_user(uid=uid)
    temp = get_percentage(right=user["right_solved"], solved=user["solved"])
    text = (
        '<b>Твой профиль</b> 😀 \n'
        '----------\n'
        f'<b>Имя</b>: {user["name"]}\n'
        f'<b>Баланс</b>: {user["balance"]} руб.\n'
        f'<b>Класс</b>: {user["grade"]}\n'
        f'<b>Решено верно</b>: {user["right_solved"]} ({temp}%)\n'
    )
    kbd = await get_inline(
        btns={
            'Пополнить баланс 💰': 'deposit',
            '⬅️ Назад': 'main_menu',
        },
        sizes=(1, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "support")
async def menu_support(callback: CallbackQuery):
    text = (f"При возникновении проблем обращаться к @delotbtw")
    kbd = await get_inline(
        btns={
            "⬅️ Главное меню": "main_menu",
        },
        sizes=(1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "choose_tamplate_tasks")
async def menu_template_tasks(callback: CallbackQuery):
    text = ("⬇️ Часть экзамена")
    kbd = await get_inline(
        btns={
            "Аудирование 🎧": "part_audio",
            "Чтение 📖": "part_reading",
            "Лексика и грамматика 📚": "part_grammar",
            "Письмо ✍️": "part_mail",
            "⬅️ Назад": "main_menu",
        },
        sizes=(2, 2, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "choose_essay")
async def menu_check_mail(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # отчистка состояния при отмене проверки письма
    text = ("Ух ты, уже есть написанный текст? Круто! \nКакой тип проверки выберешь?")
    kbd = await get_inline(
        btns={
            "Проверка нейросетью 🤖": "check_by_ai",
            "Проверка экспертом 👨‍🏫": "check_by_expert",
            "⬅️ Назад": "main_menu",
        },
        sizes=(1, 1, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "check_by_ai")
async def check_by_ai(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CheckMail.check_type)
    await state.update_data(check_type='ai')
    text = ("⬇️ Выбери задание, которое хочешь проверить ")
    kbd = await get_inline(
        btns={
            '37': 'choice_37_ai',
            '38': 'choice_38_ai',
            'Назад': 'choose_essay',
        },
        sizes=(2, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


# * Проверка эссе из задания 38
@user_router.callback_query(F.data == 'choice_38_ai')
async def choice_38_ai(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CheckEssay.check_type)
    await state.update_data(task_type='ai')
    text = ('Подтверждай покупку ниже и мы начианем 💥')
    kbd = await get_inline(
        btns={
            'Подтверждаю ✅': 'confirm_ai_38',
            'Отмена ❌': 'choose_essay',
        },
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'confirm_ai_38')
async def confirm_check_38_ai(callback: CallbackQuery, state: FSMContext):
    user = await get_user(uid=callback.from_user.id)
    if int(user["balance"]) >= 49:
        await state.set_state(CheckEssay.confirmed)
        await state.update_data(confirmed='confirmed')
        await state.set_state(CheckEssay.send_photo)
        await debit_money(uid=callback.from_user.id, amount=49)
        text = ('Деньги списаны с баланса! Отправь мне фотографию с заданием 38.1 или 38.2 и инфографикой. Пример - https://share.cleanshot.com/X1J421Nf')
        await callback.message.edit_text(text=text)
        await callback.answer()
    else:
        text = (f'❗ <b>Недостаточно средств</b> на балансе: {user["balance"]}\n'
                'Переходи в главное меню, чтобы пополнить баланс в Профиле')
        kbd = await get_inline(
            btns={
                '⬅️ В главное меню': 'main_menu',
            },
            sizes=(1, )
        )
        await callback.message.edit_text(text=text, reply_markup=kbd)


@user_router.message(F.photo, CheckEssay.send_photo)
async def get_photo_info(message: Message, state: FSMContext):
    await state.set_state(CheckEssay.info_from_photo)
    photo = message.photo[-1]  # type: ignore
    file_info = await bot.get_file(photo.file_id)
    file_path = os.path.join("photos", f"{photo.file_id}.jpg")
    await bot.download_file(file_info.file_path, destination=file_path)
    photo_path = f'./{file_path}'
    info_from_photo = await get_info_from_photo(photo_path=photo_path)
    await state.update_data(info_from_photo=info_from_photo)
    await state.set_state(CheckEssay.photo_path)
    await state.update_data(photo_path=photo_path)
    text = ('Я получил и распознал твои фото, теперь отправляй мне эссе!')
    await state.set_state(CheckEssay.send_essay)
    await message.answer(text=text)


@user_router.message(F.text, CheckEssay.send_essay)
async def check_essay(message: Message, state: FSMContext):
    mail_text = message.text
    data = await state.get_data()
    info_from_photo = data["info_from_photo"]

    chatgpt_answer = await get_score_38(mail_text=mail_text, info_from_photo=info_from_photo)
    clear_asnwer = chatgpt_answer.replace('**', '')

    text = (f'<b>Оценка твоего эссе:</b> ⤵️ \n---------- \n<blockquote>{clear_asnwer}</blockquote> \n')
    text_1 = 'Вернуться в главное меню?'
    kbd = await get_inline(
        btns={
            '⬅️ В главное меню': 'main_menu',
        },
        sizes=(1, )
    )
    await message.answer(text=text)
    await message.answer(text=text_1, reply_markup=kbd)


# * Все обработчики, связанные с проверкой 37 задания через CHATGPT
@user_router.callback_query(F.data == 'choice_37_ai')
async def confirm_check_37_ai(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CheckMail.task_type)
    await state.update_data(task_type='mail')
    text = ('Подтверждай покупки ниже и мы начианем 💥')
    kbd = await get_inline(
        btns={
            'Подтверждаю ✅': 'confirm_ai_37',
            'Отмена ❌': 'choose_essay',
        },
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'confirm_ai_37')
async def check_37(callback: CallbackQuery, state: FSMContext):
    user = await get_user(uid=callback.from_user.id)

    if int(user["balance"]) >= 49:
        await state.set_state(CheckMail.confirmed)
        await state.update_data(confirmed='1')
        await debit_money(uid=callback.from_user.id, amount=49)
        text = ('Окей, деньги с баланса списаны. \nОтправляй мне письмо.')
        await callback.message.answer(text=text)
    else:
        text = (f'❗ <b>Недостаточно средств</b> на балансе: {user["balance"]}\n'
                'Переходи в главное меню, чтобы пополнить баланс в Профиле')
        kbd = await get_inline(
            btns={
                '⬅️ В главное меню': 'main_menu',
            },
            sizes=(1, )
        )
        await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.message(CheckMail.confirmed, F.text)
async def get_ai_score_37(message: Message, state: FSMContext):
    chatgpt_answer = await get_score_37(mail_text=message.text)
    clear_asnwer = chatgpt_answer.replace('**', '')
    text = (f'<b>Оценка твоего письма:</b> ⤵️ \n---------- \n<blockquote>{clear_asnwer}</blockquote> \n')
    text_1 = 'Вернуться в главное меню?'
    kbd = await get_inline(
        btns={
            '⬅️ В главное меню': 'main_menu',
        },
        sizes=(1, )
    )

    await state.set_state(CheckMail.check_done)
    await state.update_data(check_done='1')
    await insert_ai_mail_check(
        uid=message.from_user.id,
        type='mail',
        content=message.text,
        score=clear_asnwer,
        status=1
    )
    await message.answer(text=text)
    await message.answer(text=text_1, reply_markup=kbd)


# * Типовое задание: аудирование
@user_router.callback_query(F.data == 'part_audio')
async def choice_audio_div(callback: CallbackQuery, state: FSMContext):
    text = 'Хорошо, выбери конкретное задание:'
    await state.set_state(SolveTasksCategory.audio)
    kbd = await get_inline(
        btns={
            'Понимание основного содержания (1)': 'audio@main_content',
            'True, false, not stated (2)': 'audio@TFNS_search',
            'Полное понимание речи (3-9)': 'audio@full_understanding',
            'Назад': 'choose_tamplate_tasks',
        },
        sizes=(1, 1, 1, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data.startswith('new@'), SolveTasksCategory.audio)
@user_router.callback_query(F.data.startswith('audio@'), SolveTasksCategory.audio)
async def send_audio_task(callback: CallbackQuery):
    await callback.message.delete()
    category = str(callback.data.split('@')[-1])
    task = await get_random_task(type=category)
    text = (
        f'<b>Задание {task["id"]}</b> \n'
        '---------- \n'
        f'<blockquote>{task["descr"]}</blockquote>\n'
        f'<b>Ссылка на аудио:</b> {task["descr_url"]} \n'
        f'<b>Ответ:</b> <tg-spoiler>{task["ans"]}</tg-spoiler>'
    )
    kbd = await get_inline(
        btns={
            '✅': 'right',
            '❌': 'wrong',
            'Новое задание 🆕': f'new@{category}',
            'Назад': 'part_audio',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


# * Типовое задание: чтение
@user_router.callback_query(F.data == 'part_reading')
async def choice_reading_div(callback: CallbackQuery, state: FSMContext):
    text = 'Хорошо, выбери конкретное задание:'
    kbd = await get_inline(
        btns={
            'Соответствие заголовок-текст (10)': 'reading@match',
            'Вставка конструкций в текст (11)': 'reading@insert',
            'Текст и 1 правильный ответ из 4 (12-18)': 'reading@choice_right',
            'Назад': 'choose_tamplate_tasks',
        },
        sizes=(1, 1, 1, 1,)
    )
    await state.set_state(SolveTasksCategory.reading)
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data.startswith('new@'), SolveTasksCategory.reading)
@user_router.callback_query(F.data.startswith('reading@'), SolveTasksCategory.reading)
async def send_reading_task(callback: CallbackQuery):
    await callback.message.delete()
    category = str(callback.data.split('@')[-1])
    print(category)
    task = await get_random_task(type=category)
    text = (
        f'<b>Задание {task["id"]}</b> \n'
        '---------- \n'
        f'<blockquote>{task["descr"]}</blockquote>\n'
        f'<b>Ответ:</b> <tg-spoiler>{task["ans"]}</tg-spoiler>'
    )
    kbd = await get_inline(
        btns={
            '✅': 'right',
            '❌': 'wrong',
            'Новое задание 🆕': f'new@{category}',
            'Назад': 'part_reading',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


# * Типовое задание: лексика и грамматика
@user_router.callback_query(F.data == 'part_grammar')
async def choice_grammar_div(callback: CallbackQuery, state: FSMContext):
    text = 'Хорошо, выбери конкретное задание:'
    kbd = await get_inline(
        btns={
            'Грамматика слов (19-24)': 'grammar@grammar',
            'Грамматика и лексика слов (25-36)': 'grammar@vocabulary',
            'Назад': 'choose_tamplate_tasks',
        },
        sizes=(1, 1, 1,)
    )
    await state.set_state(SolveTasksCategory.grammar)
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data.startswith('new@'), SolveTasksCategory.grammar)
@user_router.callback_query(F.data.startswith('grammar@'), SolveTasksCategory.grammar)
async def send_grammar_task(callback: CallbackQuery):
    await callback.message.delete()
    category = str(callback.data.split('@')[-1])
    task = await get_random_task(type=category)
    text = (
        f'<b>Задание {task["id"]}</b> \n'
        '---------- \n'
        f'<blockquote>{task["descr"]}</blockquote>\n'
        f'<b>Ответ:</b> <tg-spoiler>{task["ans"]}</tg-spoiler>'
    )
    kbd = await get_inline(
        btns={
            '✅': 'right',
            '❌': 'wrong',
            'Новое задание 🆕': f'new@{category}',
            'Назад': 'part_grammar',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


# * Типовое задание: письмо/эссе
@user_router.callback_query(F.data == 'part_mail')
async def choice_mail_div(callback: CallbackQuery, state: FSMContext):
    text = 'Хорошо, выбери конкретное задание:'
    kbd = await get_inline(
        btns={
            'Письмо (37)': 'mail@mail',
            'Эссе (38)': 'mail@essay',
            'Назад': 'choose_tamplate_tasks',
        },
        sizes=(1, 1, 1,)
    )
    await state.set_state(SolveTasksCategory.mails)
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data.startswith('new@'), SolveTasksCategory.mails)
@user_router.callback_query(F.data.startswith('mail@'), SolveTasksCategory.mails)
async def send_mails_task(callback: CallbackQuery):
    await callback.message.delete()
    category = str(callback.data.split('@')[-1])
    task = await get_random_task(type=category)
    text = (
        f'<b>Задание {task["id"]}</b> \n'
        '---------- \n'
        f'<blockquote>{task["descr"]}</blockquote>\n'
    )
    kbd = await get_inline(
        btns={
            'Новое задание 🆕': f'new@{category}',
            'Назад': 'part_mail',
        },
        sizes=(1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


# * Верно-неверно решено задание
@user_router.callback_query(F.data == 'right')
async def solve_right(callback: CallbackQuery):
    await write_solve(uid=callback.from_user.id, solved=1, right_solved=1)
    await callback.answer(text='Записано')


@user_router.callback_query(F.data == 'wrong')
async def solve_wrong(callback: CallbackQuery):
    logger.info(f"Получен callback | {callback.from_user.id} | {callback.data} ")
    await write_solve(uid=callback.from_user.id, solved=1, right_solved=0)
    await callback.answer(text='Записано')


#! Заглушки на кнопки
@user_router.callback_query(F.data == "check_by_expert")
async def check_by_expert(callback: CallbackQuery):
    text = ('🕓 Скоро сделаем, пока можно проверить свое письмо с помощью нашей нейросети!')
    kbd = await get_inline(
        btns={
            "Проверить нейросетью 🤖": "check_by_ai",
            "⬅️ Главное меню": "main_menu",
        },
        sizes=(1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "deposit")
async def deposit_start(callback: CallbackQuery):
    text = ('Скоро, пока недоступно 🕓')
    kbd = await get_inline(
        btns={
            "⬅️ Главное меню": "main_menu",
        },
        sizes=(1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "variant")
async def done_variants(callback: CallbackQuery):
    text = ('Скоро, пока недоступно 🕓')
    kbd = await get_inline(
        btns={
            "⬅️ Главное меню": "main_menu",
        },
        sizes=(1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "variant_random")
async def random_variant(callback: CallbackQuery):
    text = ('Скоро, пока недоступно 🕓')
    kbd = await get_inline(
        btns={
            "⬅️ Главное меню": "main_menu",
        },
        sizes=(1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()
