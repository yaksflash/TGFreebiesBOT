
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

admFoldersRouter = Router()


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


@admFoldersRouter.message(Command('del_folder'))
async def del_folder_func(message: types.Message):
    if not check_admin_status(message.from_user.id):
        return

    if message.chat.id != message.from_user.id:
        await message.answer('В лс, пожалуйста')
        return

    try:
        txt, date = message.text.split(' ')

        date = datetime.strptime(date, "%Y-%m-%d")
        date = date.strftime("%Y-%m-%d")

        if len(date) != 10:
            await message.answer('/del_folder YYYY-MM-DD')
            return

        with sqlite3.connect('database.db') as database:
            cursor = database.cursor()
            cursor.execute('SELECT * FROM folders WHERE folder_date = ?',
                       (date,))
            folder_data = cursor.fetchall()

            if not folder_data:
                await message.answer('Папки на этот день нет')
                return

            cursor.execute('DELETE FROM folders WHERE folder_date = ?', (date,))

            database.commit()
            cursor.close()

            await message.answer('Успешно')
            return

    except:
        await message.answer('/del_folder YYYY-MM-DD')
        return


@admFoldersRouter.callback_query(F.data == 'add_folder_commit')
async def add_folder_commit(query: types.CallbackQuery):
    await bot.delete_message(query.message.chat.id, query.message.message_id)

    txt1, date, txt2, link, txt3 = query.message.text.split('*')

    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute('SELECT * FROM folders WHERE folder_date = ?',
                       (date,))
        folder_data = cursor.fetchall()
        if folder_data:
            await bot.send_message(chat_id=query.message.chat.id, text='Папка на этот день уже есть')
            return

        cursor.execute('INSERT INTO folders (folder_date, folder_link) VALUES (?, ?)',
                       (date, link))
        database.commit()
        cursor.close()

        await bot.send_message(query.message.chat.id, 'Успешно')


@admFoldersRouter.callback_query(F.data == 'add_folder_cancel')
async def add_folder_cancel(query: types.CallbackQuery):
    await bot.delete_message(query.message.chat.id, query.message.message_id)


@admFoldersRouter.message(Command('add_folder'))
async def add_folder_func(message: types.Message):
    if not check_admin_status(message.from_user.id) and check_admin_status(message.from_user.id) != 'manager':
        return

    if message.chat.id != message.from_user.id:
        await message.answer('В лс, пожалуйста')
        return

    try:
        txt, date, link = message.text.split(' ')

        date = datetime.strptime(date, "%Y-%m-%d")
        date = date.strftime("%Y-%m-%d")

        if len(date) != 10:
            await message.answer('/add_folder YYYY-MM-DD <link>')
            return

        if not 'https://t.me/addlist/' in link:
            await message.answer('/add_folder YYYY-MM-DD <link>')
            return

        add_folder_text = f'''
<b>Вы уверены, что хотите добавить папку?</b>
Дата: *{date}*
Ссылка: *{link}*

⚠️ Перепроверьте данные
'''
        
        builder = InlineKeyboardBuilder()

        builder.button(text='Всё верно, добавить!', callback_data='add_folder_commit')
        builder.button(text='Отмена', callback_data='add_folder_cancel')

        add_folder_markup = builder.as_markup(resize_keyboard=True)

        await message.answer(text=add_folder_text, reply_markup=add_folder_markup, parse_mode=ParseMode.HTML)
        return
    except Exception as e:
        await message.answer('/add_folder YYYY-MM-DD <link>')
        return

