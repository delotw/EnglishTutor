from common.states_classes import Reg, CheckMail, SolveTasks
from features.chatgpt.chatgpt_func import get_score_37
from features.database.db_functions import *
from modules.keyboards.get_funcs.inline import *
from modules.keyboards.get_funcs.reply import *
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from loguru import logger


# Переменные
router = Router()
user_router = Router()
mark_down = ParseMode.MARKDOWN


@user_router.message(F.text == '/start')
async def send_welcome(message: Message):
    if await check_user_exists(uid=message.from_user.id):
        text = (f"<b>Привет, {await get_user_name(uid=message.from_user.id)} 👋</b> \nВыбери интересующий тебя раздел ниже:")
        kbd = await get_inline(
            btns={
                "Подготовка 🎯": "preparation",
                "Профиль ℹ️": "profile",
                "Поддержка ☎️": "support",
            },
            sizes=(1, 1, 1,)
        )
        await message.answer(text=text, reply_markup=kbd)
    else:
        text = ('Привет 👋, меня зовут <b>Тьютор</b>! \nПропиши /reg для регистарции!')
        await message.answer(text=text)


@user_router.message(F.text == '/reg')
async def reg_first(message: Message, state: FSMContext):
    text = ('1️⃣: Как тебя зовут?')
    await state.set_state(Reg.name)
    await message.answer(text=text)


@user_router.message(Reg.name)
async def reg_second(message: Message, state: FSMContext):
    logger.info(f"Получен message | UID: {message.from_user.id} | Введено имя ")
    await state.update_data(name=message.text)
    await state.set_state(Reg.grade)
    text = (f'2️⃣: {message.text}, в каком классе ты учишься?')
    kbd = await get_reply(
        'Прогуливаюсь мимо 🚶',
        '10',
        '11',
        sizes=(3,))
    await message.answer(text=text, reply_markup=kbd)


@user_router.message(Reg.grade)
async def reg_third(message: Message, state: FSMContext):
    logger.info(f"Получен message | UID: {message.from_user.id} | Введен класс ")
    await state.update_data(grade=message.text)
    await state.set_state(Reg.sex)
    text = (f'3️⃣: Как мне к тебе обращаться?')
    kbd = await get_reply(
        'Господин 🤵‍♂️',
        'Госпожа 🤵‍♀️',
        sizes=(2,)
    )
    await message.answer(text=text, reply_markup=kbd)


@user_router.message(Reg.sex)
async def reg_final(message: Message, state: FSMContext):
    logger.info(f"Получен message | UID: {message.from_user.id} | Введен пол ")
    await state.update_data(sex=message.text)
    data = await state.get_data()
    uid = message.from_user.id
    name = str(data["name"])
    grade = data["grade"]
    sex = str(data["sex"])
    await create_user(uid=uid, name=name, grade=grade, sex=sex)
    text = ('🎉 <b>Регистрация успешно окончена, я рад, что мы познакомились поближе.</b> \n В качестве <b>подарка</b> тебе закинул немного баланса, чтобы ты мог протестировать нашу проверку писем нейронкой.\n----------\n➡️ Нажми на кнопку ниже, чтобы перейти в главное меню!')
    kbd = await get_inline(
        btns={
            'В главное меню ✅': 'main_menu',
        },
        sizes=(1, )
    )
    await state.clear()
    await message.answer(text=text, reply_markup=kbd)


@user_router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await state.clear()  # сброс состояний пользователя
    text = (f"<b>Привет, {await get_user_name(uid=callback.from_user.id)} 👋</b> \nВыбери интересующий тебя раздел ниже:")
    kbd = await get_inline(
        btns={
            "Подготовка 🎯": "preparation",
            "Профиль ℹ️": "profile",
            "Поддержка ☎️": "support",
        },
        sizes=(1, 1, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "preparation")
async def menu_preparation(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await state.clear()
    text = ("Отлично, что же тебя интересует? 🔖")
    kbd = await get_inline(
        btns={
            "Готовые варианты 📚": "choose_exam_variants",
            "Типовые задания 📋": "choose_tamplate_tasks",
            "Проверить письмо 📝": "choose_essay",
            "⬅️ Главное меню": "main_menu"
        },
        sizes=(1, 1, 1, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "profile")
async def menu_user_profile(callback: CallbackQuery):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
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
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    text = (f"При возникновении проблем обращаться к @delotbtw")
    kbd = await get_inline(
        btns={
            "⬅️ Главное меню": "main_menu",
        },
        sizes=(1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "choose_exam_variants")
async def menu_exam_variants(callback: CallbackQuery):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")

    text = ("🎲 Так, ну выбор за тобой!")
    kbd = await get_inline(
        btns={
            "Вариант 1": "variant",
            "Вариант 2": "variant",
            "⬅️ Назад": "preparation",
        },
        sizes=(1, 1, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "choose_tamplate_tasks")
async def menu_template_tasks(callback: CallbackQuery):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    text = ("⬇️ Часть экзамена")
    kbd = await get_inline(
        btns={
            "Аудирование 🎧": "part_audirovanie",
            "Чтение 📖": "part_reading",
            "Лексика и грамматика 📚": "part_grammar",
            "Письмо ✍️": "part_mail",
            "⬅️ Назад": "preparation",
        },
        sizes=(2, 2, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "choose_essay")
async def menu_check_mail(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await state.clear()  # отчистка состояния при отмене проверки письма
    text = ("Ух ты, уже есть написанный текст? Круто! \nКакой тип проверки выберешь?")
    kbd = await get_inline(
        btns={
            "Проверка нейросетью 🤖": "check_by_ai",
            "Проверка экспертом 👨‍🏫": "check_by_expert",
            "⬅️ Назад": "preparation",
        },
        sizes=(1, 1, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "check_by_ai")
async def check_by_ai(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
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


# todo:  Сделать наконец эту проверку эссе
@user_router.callback_query(F.data == 'choice_38_ai')
async def confirm_check_38_ai(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await state.set_state(CheckMail.task_type)
    await state.update_data(task_type='essay')
    text = ('Скоро, пока недоступно 🕓')
    kbd = await get_inline(
        btns={
            'Назад': 'check_by_ai',
        },
        sizes=(1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


# * Все обработчики, связанные с проверкой 37 задания через CHATGPT
@user_router.callback_query(F.data == 'choice_37_ai')
async def confirm_check_37_ai(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
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
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    user = await get_user(uid=callback.from_user.id)
    kbd = await get_inline(
        btns={
            '⬅️ В главное меню': 'main_menu',
        },
        sizes=(1, )
    )
    if int(user["balance"]) >= 149:
        await state.set_state(CheckMail.confirmed)
        await state.update_data(confirmed='1')
        await debit_money(uid=callback.from_user.id, amount=149)
        text = ('Окей, деньги с баланса списаны. \nОтправляй мне письмо.')
        await callback.message.answer(text=text)
    else:
        text = (f'❗ <b>Недостаточно средств</b> на балансе: {user["balance"]}\n'
                'Переходи в главное меню, чтобы пополнить баланс в Профиле')

        await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.message(CheckMail.confirmed, F.text)
async def get_ai_score_37(message: Message, state: FSMContext):
    logger.info(f"Получен message | UID: {message.from_user.id} | Письмо на оценку ")

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


# * Обработчики всего, что связано с типовыми заданиями по аудированию
@user_router.callback_query(F.data == 'part_audirovanie')
async def choice_audio_div(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    text = 'Хорошо, выбери конкретное задание:'
    await state.set_state(SolveTasks.solve_audio)
    kbd = await get_inline(
        btns={
            'Понимание основного содержания (1)': 'audio_main_content',
            'True, false, not stated (2)': 'audio_TFNS_search',
            'Полное понимание речи (3-9)': 'audio_full_understanding',
            'Назад': 'choose_tamplate_tasks',
        },
        sizes=(1, 1, 1, 1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'new', SolveTasks.solve_main_content)
@user_router.callback_query(F.data == 'audio_main_content')
async def audio_main_content(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await callback.message.delete()
    await state.set_state(SolveTasks.solve_main_content)
    task = await get_random_task(type='main_content')
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
            'Новое задание 🆕': 'new',
            'Назад': 'part_audirovanie',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'new', SolveTasks.solve_TFNS_search)
@user_router.callback_query(F.data == 'audio_TFNS_search')
async def audio_TFNS_search(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await callback.message.delete()
    await state.set_state(SolveTasks.solve_TFNS_search)
    task = await get_random_task(type='TFNS_search')
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
            'Новое задание 🆕': 'new',
            'Назад': 'part_audirovanie',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'new', SolveTasks.solve_full_understanding)
@user_router.callback_query(F.data == 'audio_full_understanding')
async def audio_full_understanding(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await callback.message.delete()
    await state.set_state(SolveTasks.solve_full_understanding)
    task = await get_random_task(type='full_understanding')
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
            'Новое задание 🆕': 'new',
            'Назад': 'part_audirovanie',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


# * Обработчики всего, что связано с типовыми заданиями по чтению
@user_router.callback_query(F.data == 'part_reading')
async def choice_reading_div(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    text = 'Хорошо, выбери конкретное задание:'
    kbd = await get_inline(
        btns={
            'Соответствие заголовок-текст (10)': 'reading_match',
            'Вставка конструкций в текст (11)': 'reading_insert',
            'Текст и 1 правильный ответ из 4 (12-18)': 'reading_choice_right',
            'Назад': 'choose_tamplate_tasks',
        },
        sizes=(1, 1, 1, 1,)
    )
    await state.set_state(SolveTasks.solve_reading)
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'new', SolveTasks.solve_match)
@user_router.callback_query(F.data == 'reading_match')
async def reading_match(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await callback.message.delete()
    await state.set_state(SolveTasks.solve_match)
    task = await get_random_task(type='match')
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
            'Новое задание 🆕': 'new',
            'Назад': 'part_reading',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'new', SolveTasks.solve_insert)
@user_router.callback_query(F.data == 'reading_insert')
async def reading_insert(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await callback.message.delete()
    await state.set_state(SolveTasks.solve_insert)
    task = await get_random_task(type='insert')
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
            'Новое задание 🆕': 'new',
            'Назад': 'part_reading',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'new', SolveTasks.solve_choice_right)
@user_router.callback_query(F.data == 'reading_choice_right')
async def reading_choice_right(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await callback.message.delete()
    await state.set_state(SolveTasks.solve_choice_right)
    task = await get_random_task(type='choice_right')
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
            'Новое задание 🆕': 'new',
            'Назад': 'part_reading',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


# * Обработчики всего, что связано с типовыми заданиями по грамматике
@user_router.callback_query(F.data == 'part_grammar')
async def choice_grammar_div(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    text = 'Хорошо, выбери конкретное задание:'
    kbd = await get_inline(
        btns={
            'Грамматика слов (19-24)': 'grammar_grammar',
            'Грамматика и лексика слов (25-36)': 'grammar_vocabulary',
            'Назад': 'choose_tamplate_tasks',
        },
        sizes=(1, 1, 1,)
    )
    await state.set_state(SolveTasks.solve_grammar)
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'new', SolveTasks.solve_grammar)
@user_router.callback_query(F.data == 'grammar_grammar')
async def grammar_grammar(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await callback.message.delete()
    await state.set_state(SolveTasks.solve_grammar)
    task = await get_random_task(type='grammar')
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
            'Новое задание 🆕': 'new',
            'Назад': 'part_grammar',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'new', SolveTasks.solve_vocabulary)
@user_router.callback_query(F.data == 'grammar_vocabulary')
async def grammar_vocabulary(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await callback.message.delete()
    await state.set_state(SolveTasks.solve_vocabulary)
    task = await get_random_task(type='vocabulary')
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
            'Новое задание 🆕': 'new',
            'Назад': 'part_grammar',
        },
        sizes=(2, 1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd)
    await callback.answer()


# * Обработчики всего, что связано с типовыми заданиями по написанию письма
@user_router.callback_query(F.data == 'part_mail')
async def choice_mail_div(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    text = 'Хорошо, выбери конкретное задание:'
    kbd = await get_inline(
        btns={
            'Письмо (37)': 'mail_mail',
            'Эссе (38)': 'mail_essay',
            'Назад': 'choose_tamplate_tasks',
        },
        sizes=(1, 1, 1,)
    )
    await state.set_state(SolveTasks.solve_mails)
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == 'new', SolveTasks.solve_mail)
@user_router.callback_query(F.data == 'mail_mail')
async def mail_mail(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await callback.message.delete()
    await state.set_state(SolveTasks.solve_mail)
    task = await get_random_task(type='mail')
    text = (
        f'<b>Задание {task["id"]}</b> \n'
        '---------- \n'
        f'<blockquote>{task["descr"]}</blockquote>\n'
    )
    kbd = await get_inline(
        btns={
            'Новое задание 🆕': 'new',
            'Назад': 'part_mail',
        },
        sizes=(1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd, disable_web_page_preview=True)
    await callback.answer()


@user_router.callback_query(F.data == 'new', SolveTasks.solve_essay)
@user_router.callback_query(F.data == 'mail_essay')
async def mail_essay(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await callback.message.delete()
    await state.set_state(SolveTasks.solve_essay)
    task = await get_random_task(type='essay')
    text = (
        f'<b>Задание {task["id"]}</b> \n'
        '---------- \n'
        f'<blockquote>{task["descr"]}</blockquote>\n'
    )
    kbd = await get_inline(
        btns={
            'Новое задание 🆕': 'new',
            'Назад': 'part_mail',
        },
        sizes=(1, 1,)
    )
    await callback.message.answer(text=text, reply_markup=kbd, disable_web_page_preview=True)
    await callback.answer()


# * Обработчики верно/неверно решенных заданий
@user_router.callback_query(F.data == 'right')
async def solve_right(callback: CallbackQuery):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await write_solve(uid=callback.from_user.id, solved=1, right_solved=1)
    await callback.answer(text='Записано')


@user_router.callback_query(F.data == 'wrong')
async def solve_wrong(callback: CallbackQuery):
    logger.info(f"Получен callback | UID: {callback.from_user.id} | cb: {callback.data} ")
    await write_solve(uid=callback.from_user.id, solved=1, right_solved=0)
    await callback.answer(text='Записано')


#! Заглушки на кнопки
@user_router.callback_query(F.data == "check_by_expert")
async def check_by_expert(callback: CallbackQuery):
    text = ('Скоро, пока недоступно 🕓')
    kbd = await get_inline(
        btns={
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


@user_router.callback_query(F.data == "part_audirovanie")
async def part_audio(callback: CallbackQuery):
    text = ('Скоро, пока недоступно 🕓')
    kbd = await get_inline(
        btns={
            "⬅️ Главное меню": "main_menu",
        },
        sizes=(1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "part_grammar")
async def part_grammar(callback: CallbackQuery):
    text = ('Скоро, пока недоступно 🕓')
    kbd = await get_inline(
        btns={
            "⬅️ Главное меню": "main_menu",
        },
        sizes=(1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()


@user_router.callback_query(F.data == "part_mail")
async def part_mail(callback: CallbackQuery):
    text = ('Скоро, пока недоступно 🕓')
    kbd = await get_inline(
        btns={
            "⬅️ Главное меню": "main_menu",
        },
        sizes=(1,)
    )
    await callback.message.edit_text(text=text, reply_markup=kbd)
    await callback.answer()
