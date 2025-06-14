
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from datetime import datetime, timedelta
import sqlite3
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from aiogram.types import CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
import sqlite3
import pytz
import datetime
from datetime import datetime, timedelta
from config import TOKEN
import config
import pytz
from aiogram.fsm.state import StatesGroup, State
from loader import bot

class Set_date_giveaways_admin(StatesGroup):
    date = State()

import random

adminGiveawaysRouter = Router()


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
            

def admin_givlist(date, date_word, number):
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute('SELECT * FROM giveaways WHERE end_date = ? ORDER BY end_time', (date,))
        giveaways = cursor.fetchall()

        if not giveaways:
            return 'Розыгрышей нет'

        is_infolder = "Розыгрыш в папке! ✅" if giveaways[number][11] else "Розыгрыша нет в папке! ❌"
        is_recomended = "ДА" if giveaways[number][12] else "НЕТ" 
        is_infolder_bonus = "(не проверен)" if giveaways[number][11] == None else " "
        
        cursor.execute("SELECT * FROM giveaways WHERE end_date = ? AND is_in_folder = ?", (date, True))
        infolder_givwaways = cursor.fetchall()

        premium_gifts = 0
        stars_gifts = 0
        premium_subs = 0
        stars_count = 0
        channels_needed = 0
        for gift in infolder_givwaways:
            premium_gifts += 1 if gift[0] == 'premium' else 0
            stars_gifts += 1 if gift[0] == 'stars' else 0
            premium_subs += gift[4] if gift[0] == 'premium' else 0
            stars_count += gift[3] if gift[0] == 'stars' else 0
            channels_needed += gift[13]
        
        text = f'''
<b>Розыгрыш на {date_word}:</b>
➖➖➖➖➖➖➖➖➖

Ссылка: {giveaways[number][8]}
Время завершения: {giveaways[number][7]}
Приз: {giveaways[number][0]} ({giveaways[number][4]} winners)

{is_infolder} {is_infolder_bonus}
Рекомендованный? --> {is_recomended} 
➖➖➖➖➖➖➖➖➖

Статистика для папщика:

<code>💎 Premium: {premium_gifts} шт (подписок: {premium_subs})
⭐️ Stars: {stars_gifts} шт (звёзд: {stars_count})</code>

Каналов в папке: {channels_needed} шт.
'''
        return text

@adminGiveawaysRouter.message(Command('admin_giveaways'))
async def admin_giveaways(message: types.Message):
    if not check_admin_status(message.from_user.id):
        return

    if message.chat.id != message.from_user.id:
        await message.answer('В лс, пожалуйста')
        return

    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='📅 | Сегодня', callback_data='admin_giveaways_today'))
    keyboard.add(types.InlineKeyboardButton(text='📅 | Завтра', callback_data='admin_giveaways_tomorrow'))
    keyboard.add(types.InlineKeyboardButton(text='📅 | Выбрать дату', callback_data='admin_giveaways_choose_date'))
    keyboard.adjust(2)

    await message.answer('Выберите дату для открытия админского списка розыгрышей', reply_markup=keyboard.as_markup())



def admin_giveaways_markup(user_id, date, number):
    keyboard = InlineKeyboardBuilder()
    
    number = int(number)
    modified = False

    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()
        cursor.execute('SELECT * FROM giveaways WHERE end_date = ? ORDER BY end_time', (date,))
        giveaways = cursor.fetchall()
    

    if len(giveaways) == 1:
        keyboard.add(types.InlineKeyboardButton(text='⬅️', callback_data=f'nonebutton'))
        keyboard.add(types.InlineKeyboardButton(text=f'{number+1}/{len(giveaways)}', callback_data=f'nonebutton'))
        keyboard.add(types.InlineKeyboardButton(text='➡️', callback_data=f'nonebutton'))
        modified = True
    else:
        if number == 0:
            keyboard.add(types.InlineKeyboardButton(text='⬅️', callback_data=f'nonebutton'))
            keyboard.add(types.InlineKeyboardButton(text=f'{number+1}/{len(giveaways)}', callback_data=f'nonebutton'))
            keyboard.add(types.InlineKeyboardButton(text='➡️', callback_data=f'admin_givlist_next {date} {number+1}'))
            modified = True
        if len(giveaways) == number+1:
            keyboard.add(types.InlineKeyboardButton(text='⬅️', callback_data=f'admin_givlist {date} {number-1}'))
            keyboard.add(types.InlineKeyboardButton(text=f'{number+1}/{len(giveaways)}', callback_data=f'nonebutton'))
            keyboard.add(types.InlineKeyboardButton(text='➡️', callback_data=f'nonebutton'))
            modified = True
    
    if not modified:
        keyboard.add(types.InlineKeyboardButton(text='⬅️', callback_data=f'admin_givlist {date} {number-1}'))
        keyboard.add(types.InlineKeyboardButton(text=f'{number+1}/{len(giveaways)}', callback_data=f'nonebutton'))
        keyboard.add(types.InlineKeyboardButton(text='➡️', callback_data=f'admin_givlist_next {date} {number+1}'))

    if check_admin_status(user_id) == "manager":
        keyboard.add(types.InlineKeyboardButton(text='📁', callback_data=f'admgiv_infolder {date} {number}'))
        
    elif check_admin_status(user_id):
        keyboard.add(types.InlineKeyboardButton(text='📁', callback_data=f'admgiv_infolder {date} {number}'))
        keyboard.add(types.InlineKeyboardButton(text='🚀', callback_data=f'admgiv_recomendstatus {date} {number}'))
    

    keyboard.adjust(3, 2)
    return keyboard

@adminGiveawaysRouter.callback_query(F.data.startswith('admgiv_infolder'))
async def admin_giv_recomendstatus_function(query: CallbackQuery, state: FSMContext):
    if not check_admin_status(query.from_user.id):
        return

    if query.message.chat.id != query.from_user.id:
        await query.answer('В лс, пожалуйста')
        return
    
    _, date, number = query.data.split()
    number = int(number)
    date = datetime.strptime(date, "%Y-%m-%d").date()
    date_word = date.strftime("%Y-%m-%d")

    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()
        cursor.execute('SELECT * FROM giveaways WHERE end_date = ? ORDER BY end_time', (date,))
        giveaways = cursor.fetchall()
        
        cursor.execute("UPDATE giveaways SET is_in_folder = ? WHERE giveaway_link = ?", (not giveaways[number][11], giveaways[number][8]))   
        database.commit()
    
    text = admin_givlist(date, date_word, number)

    keyboard = admin_giveaways_markup(query.from_user.id, date, number)

    await bot.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard.as_markup(), chat_id=query.message.chat.id, message_id=query.message.message_id)

    

@adminGiveawaysRouter.callback_query(F.data.startswith('admgiv_recomendstatus'))
async def admin_giv_recomendstatus_function(query: CallbackQuery, state: FSMContext):
    if not check_admin_status(query.from_user.id):
        return

    if query.message.chat.id != query.from_user.id:
        await query.answer('В лс, пожалуйста')
        return
    
    _, date, number = query.data.split()
    number = int(number)
    date = datetime.strptime(date, "%Y-%m-%d").date()
    date_word = date.strftime("%Y-%m-%d")

    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()
        cursor.execute('SELECT * FROM giveaways WHERE end_date = ? ORDER BY end_time', (date,))
        giveaways = cursor.fetchall()
        
        cursor.execute("UPDATE giveaways SET is_recomended = ? WHERE giveaway_link = ?", (not giveaways[number][12], giveaways[number][8]))   
        database.commit()
    
    text = admin_givlist(date, date_word, number)

    keyboard = admin_giveaways_markup(query.from_user.id, date, number)

    await bot.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard.as_markup(), chat_id=query.message.chat.id, message_id=query.message.message_id)

    

@adminGiveawaysRouter.callback_query(F.data.startswith('admin_giveaways'))
async def admin_giveaways_function(query: CallbackQuery, state: FSMContext):
    if not check_admin_status(query.from_user.id):
        return

    if query.message.chat.id != query.from_user.id:
        await query.answer('В лс, пожалуйста')
        return

    await state.clear()

    date = datetime.now(pytz.timezone('Europe/Moscow')).date()
    date_word = date.strftime("%Y-%m-%d")

    if query.data == 'admin_giveaways_today':
        date = datetime.now(pytz.timezone('Europe/Moscow')).date()
        date_word = date.strftime("%Y-%m-%d")
        number = 0
    elif query.data == 'admin_giveaways_tomorrow':
        date = datetime.now(pytz.timezone('Europe/Moscow')).date() + timedelta(days=1)
        date_word = date.strftime("%Y-%m-%d")
        number = 0
    elif query.data == 'admin_giveaways_choose_date':
        await state.set_state(Set_date_giveaways_admin.date)
        await query.message.answer('Введите дату в формате YYYY-MM-DD')
        return

    text = admin_givlist(date, date_word, number)

    keyboard = admin_giveaways_markup(query.from_user.id, date, number)

    await bot.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard.as_markup(), chat_id=query.message.chat.id, message_id=query.message.message_id)


@adminGiveawaysRouter.callback_query(F.data.startswith('admin_givlist'))
async def admin_giveaways_function(query: CallbackQuery, state: FSMContext):
    if not check_admin_status(query.from_user.id):
        return

    if query.message.chat.id != query.from_user.id:
        await query.answer('В лс, пожалуйста')
        return

    await state.clear()

    _, date, number = query.data.split()
    number = int(number)
    date = datetime.strptime(date, "%Y-%m-%d").date()
    date_word = date.strftime("%Y-%m-%d")

    text = admin_givlist(date, date_word, number)

    keyboard = admin_giveaways_markup(query.from_user.id, date, number)

    await bot.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard.as_markup(), chat_id=query.message.chat.id, message_id=query.message.message_id)


@adminGiveawaysRouter.message(Set_date_giveaways_admin.date)
async def process_custom_date_input(message: Message, state: FSMContext):
    user_input = message.text.strip()

    try:
        date = datetime.strptime(user_input, "%Y-%m-%d").date()
    except ValueError:
        await message.answer("❌ Неверный формат даты. Введите в формате YYYY-MM-DD.")
        return

    await state.clear()

    date_word = date.strftime("%Y-%m-%d")
    number = 0

    text = admin_givlist(date, date_word, number)

    keyboard = admin_giveaways_markup(message.from_user.id, date, number)

    await message.answer(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard.as_markup())
    
