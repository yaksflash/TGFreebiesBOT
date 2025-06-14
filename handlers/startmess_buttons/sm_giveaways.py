
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


smGiveawayRouter = Router()


class Set_folder_time(StatesGroup):
    folder_time = State()

class Set_date_giveaways(StatesGroup):
    date = State()


# ~~~~~~~~~~ GIVEAWAYS (LIST) ~~~~~~~~~~


def get_givlist(date, date_word):
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute('SELECT * FROM giveaways WHERE end_date = ? ORDER BY end_time', (date,))
        giveaways = cursor.fetchall()

        if not giveaways:
            return 'Розыгрышей нет'

        text = f'''
*— 🎁 | Розыгрыши на {date_word}: *
➖➖➖➖➖➖➖➖➖

'''

        prem_sum = 0
        star_sum = 0
        for gift in giveaways:
            if gift[0] == 'stars':
                star_sum += gift[3]
                prize = f'[{gift[3]} звёзд]({gift[8]}) — {gift[4]} чел'
            else:
                prem_sum += gift[4]
                if gift[4] > 10 and gift[4] < 20:
                    subword = 'подписок'
                else:
                    if gift[4] % 10 == 0 or gift[4] % 10 == 5 or gift[4] % 10 == 6 or gift[4] % 10 == 7 or gift[4] % 10 == 8 or gift[4] % 10 == 9:
                        subword = 'подписок'
                    elif gift[4] % 10 == 1:
                        subword = 'подписка'
                    elif gift[4] % 10 == 2 or gift[4] % 10 == 3 or gift[4] % 10 == 4:
                        subword = 'подписки'

                prize = f'[{gift[4]} {subword}]({gift[8]}) — {gift[5]} мес'
            if date_word == "сегодня" or date_word == "завтра":
                if gift[11] == None:
                    folder_symbol = "👁‍🗨"
                elif gift[11] == False:
                    folder_symbol = "⚠️"
                else:
                    folder_symbol = "📂"
                if gift[12]:
                    folder_symbol = f"🚀 {folder_symbol}"
                text += f'{folder_symbol} - {gift[7]} | {prize} \n'
            else:
                if gift[12]:
                    text += f'🚀 - {gift[7]} | {prize} \n'
                else:
                    text += f'{gift[7]} | {prize} \n'

        text += f'''
Премиумов: {prem_sum}
Звёзд: {star_sum}
'''
        return text

@smGiveawayRouter.message(Set_date_giveaways.date)
async def nday_glist(message: Message, state: FSMContext):
    await state.clear()
    build = InlineKeyboardBuilder()
    build.button(text='Сегодняшние', callback_data='qglist_today')
    build.button(text='Завтрашние', callback_data='qglist_tomorrow')
    build.button(text='На другой день', callback_data='qglist_nday')
    build.button(text='назад в меню', callback_data='qback_to_start_menu')
    build.adjust(2, 1, 1)

    givlist_markup = build.as_markup()

    await message.answer(get_givlist(message.text, message.text), parse_mode=ParseMode.MARKDOWN, reply_markup=givlist_markup)



@smGiveawayRouter.callback_query(F.data.startswith('qglist'))
async def qgivlist_function(query: CallbackQuery, state: FSMContext):
    chat_id = query.message.chat.id

    build = InlineKeyboardBuilder()

    build.button(text='Сегодняшние', callback_data='qglist_today')
    build.button(text='Завтрашние', callback_data='qglist_tomorrow')
    build.button(text='На другой день', callback_data='qglist_nday')
    build.button(text='назад в меню', callback_data='back_to_start_menu')
    build.adjust(2, 1, 1)

    givlist_markup = build.as_markup()

    if 'today' in str(query.data):
        date = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d')
        await bot.edit_message_text(text=get_givlist(date, 'сегодня'), message_id=query.message.message_id, chat_id=query.message.chat.id,
                              parse_mode=ParseMode.MARKDOWN, reply_markup=givlist_markup)

    elif 'tomorrow' in str(query.data):
        date = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=1)).strftime('%Y-%m-%d')
        await bot.edit_message_text(text=get_givlist(date, 'завтра'), message_id=query.message.message_id, chat_id=query.message.chat.id,
                              parse_mode=ParseMode.MARKDOWN, reply_markup=givlist_markup)

    elif 'nday' in str(query.data):
        await bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text='Отправьте дату в формате (YYYY-MM-DD), на которую вы хотите получить список розыгрышей', reply_markup=givlist_markup, parse_mode=ParseMode.HTML)
        await state.set_state(Set_date_giveaways.date)


@smGiveawayRouter.callback_query(F.data.startswith('startmess-giveaway'))
async def startmess_givlist_function(query: CallbackQuery, state: FSMContext):
    build = InlineKeyboardBuilder()

    build.button(text='Сегодняшние', callback_data='qglist_today')
    build.button(text='Завтрашние', callback_data='qglist_tomorrow')
    build.button(text='На другой день', callback_data='qglist_nday')
    build.button(text='назад в меню', callback_data='back_to_start_menu')
    build.adjust(2, 1, 1)

    givlist_markup = build.as_markup(resize_keyboard=True)

    givlist_text = '''
    <b>🎁 → Меню | Список розыгрышей</b>
    '''

    await bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=givlist_text, reply_markup=givlist_markup, parse_mode=ParseMode.HTML)