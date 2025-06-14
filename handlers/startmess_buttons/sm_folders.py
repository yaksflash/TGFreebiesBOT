
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
# FSM состояние
class TimeInputState(StatesGroup):
    waiting_for_time = State()

@smFoldersRouter.callback_query(F.data.startswith('startmess-folders'))
async def folders_button(query: CallbackQuery):
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        today_date = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d')
        tomorrow_date = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=1)).strftime('%Y-%m-%d')

        cursor.execute('DELETE FROM folders WHERE folder_date < ?',
                       (today_date,))

        cursor.execute('SELECT folder_link FROM folders WHERE folder_date = ?', (today_date,))
        today_folder = cursor.fetchone()
        cursor.execute('SELECT folder_link FROM folders WHERE folder_date = ?', (tomorrow_date,))
        tomorrow_folder = cursor.fetchone()


        builder = InlineKeyboardBuilder()

        if today_folder and tomorrow_folder:
            builder.button(text=f'✅ {today_date}', url=f'{today_folder[0]}')
            builder.button(text=f'✅ {tomorrow_date}', url=f'{tomorrow_folder[0]}')
        elif not today_folder and tomorrow_folder:
            builder.button(text=f'❌ {today_date}', callback_data='nofolderbutton')
            builder.button(text=f'✅ {tomorrow_date}', url=f'{tomorrow_folder[0]}')
        elif today_folder and not tomorrow_folder:
            builder.button(text=f'✅ {today_date}', url=f'{today_folder[0]}')
            builder.button(text=f'❌ {tomorrow_date}', callback_data='nofolderbutton')
            
        else:
            builder.button(text=f'❌ {today_date}', callback_data='nofolderbutton')
            builder.button(text=f'❌ {tomorrow_date}', callback_data='nofolderbutton')
        
        builder.button(text='Настройки Уведомлений', callback_data='folder_notifac_settings')
        builder.button(text='назад в меню', callback_data='back_to_start_menu')
        
        builder.adjust(2, 1, 1)
        folder_markup = builder.as_markup(resize_keyboard=True)

        folder_text = '''
<b>Папки с розыгрышами</b>
'''
    
        await bot.edit_message_text(text=folder_text, parse_mode=ParseMode.HTML, reply_markup=folder_markup, chat_id=query.message.chat.id, message_id=query.message.message_id)


@smFoldersRouter.callback_query(F.data.startswith('folder_notifac_settings'))
async def folders_button(query: CallbackQuery):
    user_id = query.from_user.id
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute("SELECT * FROM notifications WHERE id = ?", (user_id,))
        user_notifac_data = cursor.fetchall()

        if not user_notifac_data:
            cursor.execute("INSERT INTO notifications (id, do_mall, mall_time) VALUES (?, ?, ?)", (user_id, False, None))
            database.commit
            cursor.execute("SELECT * FROM notifications WHERE id = ?", (user_id,))
            user_notifac_data = cursor.fetchall()
        
        user_data = user_notifac_data[0]

        if user_data[1]:
            do_mall = "включена"
            button_text1 = "Выключить рассылку"
        else:
            do_mall = "выключена"
            button_text1 = "Включить рассылку"

        if not user_data[2]:
            mall_time = "не установлено"
            button_text2 = "Установить время рассылки"
        else:
            mall_time = user_data[2]
            button_text2 = "Изменить время рассылки"

        notifac_text = f'''
--- Уведомления о папках ---
Рассылка: {do_mall}
Время рассылки: {mall_time}
'''
        
        build = InlineKeyboardBuilder()
        build.button(text=f'{button_text1}', callback_data='change_folder_notifac_status')
        build.button(text=f'{button_text2}', callback_data='change_folder_notifac_time')
        build.button(text='назад в меню', callback_data='back_to_start_menu')
        build.adjust(1)
        notifac_setting_markup = build.as_markup(resize_keyboard=True)
        await bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=notifac_text, reply_markup=notifac_setting_markup)


@smFoldersRouter.callback_query(F.data.startswith('change_folder_notifac_status'))
async def folders_button(query: CallbackQuery):
    user_id = query.from_user.id
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute("SELECT * FROM notifications WHERE id = ?", (user_id,))
        user_notifac_data = cursor.fetchall()

        if not user_notifac_data:
            cursor.execute("INSERT INTO notifications (id, do_mall, mall_time) VALUES (?, ?, ?)", (user_id, False, None))
            database.commit
            cursor.execute("SELECT * FROM notifications WHERE id = ?", (user_id,))
            user_notifac_data = cursor.fetchall()

        user_data = user_notifac_data[0]

        new_status = not user_data[1]

        cursor.execute("UPDATE notifications SET do_mall = ? WHERE id = ?", (new_status, user_id))
        cursor.execute("SELECT * FROM notifications WHERE id = ?", (user_id,))
        user_notifac_data = cursor.fetchall()
        user_data = user_notifac_data[0]

        if user_data[1]:
            do_mall = "включена"
            button_text1 = "Выключить рассылку"
        else:
            do_mall = "выключена"
            button_text1 = "Включить рассылку"

        if not user_data[2]:
            mall_time = "не установлено"
            button_text2 = "Установить время рассылки"
        else:
            mall_time = user_data[2]
            button_text2 = "Изменить время рассылки"

        notifac_text = f'''
--- Уведомления о папках ---
Рассылка: {do_mall}
Время рассылки: {mall_time}
'''
        
        build = InlineKeyboardBuilder()
        build.button(text=f'{button_text1}', callback_data='change_folder_notifac_status')
        build.button(text=f'{button_text2}', callback_data='change_folder_notifac_time')
        build.button(text='назад в меню', callback_data='back_to_start_menu')
        build.adjust(1)
        notifac_setting_markup = build.as_markup(resize_keyboard=True)
        await bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=notifac_text, reply_markup=notifac_setting_markup)


# Обработка нажатия на кнопку "изменить время"
@smFoldersRouter.callback_query(F.data.startswith('change_folder_notifac_time'))
async def folders_button(query: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await query.message.answer("Введите время (любое после 18:00 по МСК), например: 18:30")
    await state.set_state(TimeInputState.waiting_for_time)

# Обработка текстового сообщения (ожидаем время)
@smFoldersRouter.message(TimeInputState.waiting_for_time)
async def handle_time_input(message: Message, state: FSMContext):
    if message.text.startswith("/"):
        await state.clear()
        await message.answer("Обнаружена команда. Время не изменено.")
        return

    user_input = message.text.strip()

    try:
        parsed_time = datetime.strptime(user_input, "%H:%M").time()
    except ValueError:
        await message.answer("Неверный формат. Введите время в формате HH:MM, например: 18:30")
        return

    if parsed_time < time(18, 0):
        await message.answer("Время должно быть после 18:00 по МСК. Попробуйте ещё раз.")
        return

    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()
        cursor.execute("UPDATE notifications SET mall_time = ? WHERE id = ?", (parsed_time.strftime('%H:%M'), message.from_user.id))

    await message.answer(f"Время установлено на {parsed_time.strftime('%H:%M')}")
    await state.clear()

# Обработка любых других callback-кнопок в состоянии ожидания времени
@smFoldersRouter.callback_query(TimeInputState.waiting_for_time)
async def cancel_time_input_on_other_button(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.answer()
    await query.message.answer("Операция отменена. Вы нажали другую кнопку.")