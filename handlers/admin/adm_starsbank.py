
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from datetime import datetime, time, timedelta
import sqlite3
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from loader import bot
import pytz

from aiogram.types import FSInputFile

from config import CHANNEL_CHAT_USERNAME, ADMIN_USERNAME
from config import ADMIN_STARS_GROUP
smFoldersRouter = Router()
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import STATUS_OF_CODE
starsbankRouter = Router()


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
            return False
    
@starsbankRouter.message(Command('add_starsbank'))
async def add_starsbank_admin(message: types.Message):
    if not check_admin_status(message.from_user.id):
        return
    
    if message.chat.id != message.from_user.id:
        await message.answer('В лс, пожалуйста')
        return
    
    try:
        _, stars_count, is_able = message.text.split(' ')
    except:
        await message.answer('Используйте: /del_starsbank <количество> <is_able>')
        return
    
    if is_able != STATUS_OF_CODE:
        await message.answer('is_able должен быть нужным статусом для админа (iphone)')
        return
    
    if int(stars_count) > 100:
        await message.answer('Слишком много звёзд, ты точно админ?)')
        return
    
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute("SELECT count FROM starsbank")
        starsbank = cursor.fetchone()[0]
        cursor.execute("UPDATE starsbank SET count = ?", (starsbank + int(stars_count),))
        database.commit()

    await message.answer(f'Казна бота пополнена на {stars_count} звёзд! Теперь в ней {starsbank + int(stars_count)} звёзд')

@starsbankRouter.message(Command('del_starsbank'))
async def add_starsbank_admin(message: types.Message):
    if not check_admin_status(message.from_user.id):
        return
    
    if message.chat.id != message.from_user.id:
        await message.answer('В лс, пожалуйста')
        return
    
    try:
        _, stars_count, is_able = message.text.split(' ')
    except:
        await message.answer('Используйте: /add_starsbank <количество> <is_able>')
        return
    
    if is_able != STATUS_OF_CODE:
        await message.answer('is_able должен быть нужным статусом для админа (iphone)')
        return
    
    if int(stars_count) :
        await message.answer('Включи математику! Казна не может быть отрицательной')
        return
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute("SELECT count FROM starsbank")
        starsbank = cursor.fetchone()[0]
        if starsbank - int(stars_count) < 0:
            await message.answer('Включи математику! Казна не может быть отрицательной')
            return
        
        cursor.execute("UPDATE starsbank SET count = ?", (starsbank - int(stars_count),))
        database.commit()

    await message.answer(f'Казна бота уменьшена на {stars_count} звёзд! Теперь в ней {starsbank - int(stars_count)} звёзд')
