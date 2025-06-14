from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery, FSInputFile, ContentType, chat
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import sqlite3
import pytz
import datetime
from datetime import date, datetime, timedelta
from config import TOKEN
from loader import bot
from config import FOLDER_MANAGER_ID

admFolderUpdatedRouter = Router()


def check_admin_status(user_id):
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute('SELECT status FROM users WHERE id = ?', (user_id,))
        user_status = cursor.fetchone()

        if not user_status:
            return False

        if user_status[0] == 'admin' or user_id == 929185014:
            return True
        else:
            if user_status[0] == 'manager':
                return 'manager'
            else:
                return False

@admFolderUpdatedRouter.message(Command("folder_updated_today"))
async def folder_was_updaded_admin(message: types.Message):
    if not check_admin_status(message.from_user.id):
        return
    today_date = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d')
    now_msk = datetime.now(pytz.timezone("Europe/Moscow")).strftime("%H:%M")
    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()

        cursor.execute("SELECT * FROM notifications")
        need_to_mall = cursor.fetchall()

        for user in need_to_mall:
            if not user[1]:
                continue
            try:
                await bot.send_message(user[0], f"<b>Уважаемый пользователь!</b>\nПапка на {today_date} была дополнена! Чтобы участвовать во всех розыгрышах, обновите её по той же ссылке.", parse_mode=ParseMode.HTML)
            except:
                pass

    await message.answer("Все пользователи были оповещены!")


@admFolderUpdatedRouter.message(Command("folder_updated_tomorrow"))
async def folder_was_updaded_admin(message: types.Message):
    if not check_admin_status(message.from_user.id):
        return
    tomorrow_date = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow_msk = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=1)).strftime("%H:%M")
    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()

        cursor.execute("SELECT * FROM notifications")
        need_to_mall = cursor.fetchall()

        for user in need_to_mall:
            if not user[1]:
                continue
            try:
                await bot.send_message(user[0], f"<b>Уважаемый пользователь!</b>\nПапка на {tomorrow_date} была дополнена! Чтобы участвовать во всех розыгрышах, обновите её по той же ссылке.", parse_mode=ParseMode.HTML)
            except:
                pass

    await message.answer("Все пользователи были оповещены!")