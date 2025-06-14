
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

admPromocodesRouter = Router()


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


@admPromocodesRouter.message(Command('del_promocode'))
async def del_folder_func(message: types.Message):
    if not check_admin_status(message.from_user.id):
        return

    if message.chat.id != message.from_user.id:
        await message.answer('В лс, пожалуйста')
        return

    try:
        txt, code = message.text.split(' ')

        with sqlite3.connect('database.db') as database:
            cursor = database.cursor()
            cursor.execute('SELECT * FROM promocodes WHERE code = ?',
                       (code,))
            code_data = cursor.fetchall()

            if not code_data:
                await message.answer('Такого промо нет')
                return

            cursor.execute('DELETE FROM promocodes WHERE code = ?', (code,))

            database.commit()
            cursor.close()

        await message.answer('Успешно')
        return

    except:
        await message.answer('/del_promocode code')
        return



@admPromocodesRouter.message(Command('add_promocode'))
async def add_folder_func(message: types.Message):
    if not check_admin_status(message.from_user.id) and check_admin_status(message.from_user.id) != 'manager':
        return

    if message.chat.id != message.from_user.id:
        await message.answer('В лс, пожалуйста')
        return

    try:
        txt, code, reward, r_type, activations = message.text.split(' ')

        with sqlite3.connect('database.db') as database:
            cursor = database.cursor()
            cursor.execute('SELECT * FROM promocodes WHERE code = ?',
                       (code,))
            code_data = cursor.fetchall()

            if code_data:
                await message.answer('Такой промо уже есть')
                return
            
            cursor.execute("INSERT INTO promocodes (code, used_by_ids, activations, reward, reward_type) VALUES (?, ?, ?, ?, ?)",
                           (code, " ", activations, reward, r_type))
            database.commit()

        await message.answer("Успешно!")

        

        return
    except Exception as e:
        await message.answer('/add_promocode code reward stars/sparkles activations')
        return

