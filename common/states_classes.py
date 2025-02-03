from aiogram.fsm.state import StatesGroup, State


class Reg(StatesGroup):
    name = State()
    grade = State()
    sex = State()


class BalanceDeposit(StatesGroup):
    amount = State()
    wait_confirm = State()


class CheckMail(StatesGroup):
    check_type = State()
    task_type = State()
    confirmed = State()
    send_photo = State()
    info_from_photo = State()
    photo_path = State()
    send_mail = State()
    check_done = State()


class CheckEssay(StatesGroup):
    check_type = State()
    task_type = State()
    confirmed = State()
    send_photo = State()
    info_from_photo = State()
    photo_path = State()
    send_essay = State()
    check_done = State()
    
class SolveTasksCategory(StatesGroup):
    audio = State()
    reading = State()
    grammar = State()
    mails = State()
