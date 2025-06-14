
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command

from datetime import datetime, timedelta
import sqlite3
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import pytz

from aiogram.types import FSInputFile


foldersRouter = Router()


@foldersRouter.message(Command('folders'))
async def folders_command(message: Message):
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

    folder_markup = builder.as_markup(resize_keyboard=True)

    folder_text = '''
<b>Папки с розыгрышами</b>
'''
    photo = FSInputFile(path="images/folders.jpg")
    
    await message.answer(text=folder_text, parse_mode=ParseMode.HTML, reply_markup=folder_markup)

