
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
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

activatePromocodeRouter = Router()

# Определяем состояние
class PromocodeState(StatesGroup):
    waiting_for_promocode = State()

# Обработка нажатия на кнопку
@activatePromocodeRouter.callback_query(F.data == 'activate_promocode')
async def query_activate_promocode(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Введите промокод:")
    await state.set_state(PromocodeState.waiting_for_promocode)
    await query.answer()  # Закрыть "часики" у кнопки

# Обработка ввода промокода
@activatePromocodeRouter.message(PromocodeState.waiting_for_promocode)
async def process_promocode(message: Message, state: FSMContext):
    promocode = message.text.strip()

    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()
        
        cursor.execute("SELECT * FROM promocodes WHERE code = ?", (promocode,))
        promo_data = cursor.fetchall()
    
        if not promo_data:
            await message.answer("Такого промокода не существует или достигнуто максимальное количество активаций!")
            await state.clear()
            return
        promo_data = promo_data[0]

        if promo_data[1].count("id") == promo_data[2]:
            cursor.execute("DELETE FROM promocodes WHERE code = ?", (promocode,))
            await message.answer("Такого промокода не существует или достигнуто максимальное количество активаций!")
            await state.clear()
            return
        
        if str(message.from_user.id) in promo_data[1]:
            await message.answer("Вы уже активировали данный промокод!")
            await state.clear()
            return
        
        cursor.execute("UPDATE promocodes SET used_by_ids = ? WHERE code = ?", (promo_data[1] + f" id({message.from_user.id})", promocode))

        cursor.execute("SELECT balance, stars FROM users WHERE id = ?", (message.from_user.id,))
        user_data = cursor.fetchall()[0]

        if promo_data[4] == "stars":
            cursor.execute('UPDATE users SET stars = ? WHERE id = ?', (user_data[1] + promo_data[3], message.from_user.id))
            word = "звёзд"
        elif promo_data[4] == "sparkles":
            cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (user_data[0] + promo_data[3], message.from_user.id))
            word = "звёздочек"
        
        await message.answer(f"Вы получили {promo_data[3]} {word}!")
        
    await state.clear()
