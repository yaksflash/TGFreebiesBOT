
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
from config import FOLDER_MANAGER_ID
import random

giveawaysRouter = Router()


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

            text += f'{gift[7]} | {prize} \n'

        text += f'''
Премиумов: {prem_sum}
Звёзд: {star_sum}
'''
        return text

@giveawaysRouter.message(Set_date_giveaways.date)
async def nday_glist(message: Message, state: FSMContext):
    await state.clear()
    build = InlineKeyboardBuilder()

    build.button(text='Сегодняшние', callback_data='glist_today')
    build.button(text='Завтрашние', callback_data='glist_tomorrow')
    build.button(text='На другой день', callback_data='glist_nday')

    build.adjust(2)

    givlist_markup = build.as_markup(resize_keyboard=True)

    await message.answer(get_givlist(message.text, message.text), parse_mode=ParseMode.MARKDOWN, reply_markup=givlist_markup)



@giveawaysRouter.callback_query(F.data.startswith('glist'))
async def givlist_function(query: CallbackQuery, state: FSMContext):
    chat_id = query.message.chat.id

    build = InlineKeyboardBuilder()

    build.button(text='Сегодняшние', callback_data='glist_today')
    build.button(text='Завтрашние', callback_data='glist_tomorrow')
    build.button(text='На другой день', callback_data='glist_nday')

    build.adjust(2)

    givlist_markup = build.as_markup(resize_keyboard=True)

    if 'today' in str(query.data):
        date = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d')
        await bot.edit_message_text(text=get_givlist(date, 'сегодня'), message_id=query.message.message_id, chat_id=query.message.chat.id,
                              parse_mode=ParseMode.MARKDOWN, reply_markup=givlist_markup)

    elif 'tomorrow' in str(query.data):
        date = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=1)).strftime('%Y-%m-%d')
        await bot.edit_message_text(text=get_givlist(date, 'завтра'), message_id=query.message.message_id, chat_id=query.message.chat.id,
                              parse_mode=ParseMode.MARKDOWN, reply_markup=givlist_markup)

    elif 'nday' in str(query.data):
        await bot.delete_message(query.message.chat.id, query.message.message_id)
        await bot.send_message(query.message.chat.id, text='Отправьте дату в формате (YYYY-MM-DD), на которую вы хотите получить список розыгрышей')
        await state.set_state(Set_date_giveaways.date)


@giveawaysRouter.message(Command('giveaway'))
async def giveaways_list_command(message: types.Message):
    build = InlineKeyboardBuilder()

    build.button(text='Сегодняшние', callback_data='glist_today')
    build.button(text='Завтрашние', callback_data='glist_tomorrow')
    build.button(text='На другой день', callback_data='glist_nday')
    build.adjust(2, 1)

    givlist_markup = build.as_markup(resize_keyboard=True)

    givlist_text = '''
    <b>🎁 → Меню | Список розыгрышей</b>
    '''

    await message.answer(givlist_text, reply_markup=givlist_markup, parse_mode=ParseMode.HTML)


# ~~~~~~~~~~ GIVEAWAYS (ADD) ~~~~~~~~~~


def add_giveaway(prize, special_key, countries, stars_count, winner_count, month_count, end_date, end_time, giveaway_link, user_id, added_date, channels_count):
    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        try:
            cursor.execute('INSERT INTO giveaways (prize, special_key, countries, stars_count, winner_count, month_count, end_date, end_time, giveaway_link, added_by_id, added_date, channels_count)'
                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (prize, special_key, countries, stars_count, winner_count, month_count, end_date, end_time, giveaway_link, user_id, added_date, channels_count))
            return True
        except sqlite3.IntegrityError:
            return False



@giveawaysRouter.message(F.content_type == ContentType.GIVEAWAY)
async def query_giveaway_handler(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id


    special_key = f'https://t.me/{message.forward_from_chat.id}/{message.forward_from_message_id}'

    end_data = message.giveaway.winners_selection_date

    if end_data < message.date:
        await message.reply('Данный розыгрыш завершён')
        return


    with sqlite3.connect('database.db') as database:
        cursor = database.cursor()

        cursor.execute('SELECT * FROM giveaways WHERE special_key = ?', (special_key,))
        giv_data = cursor.fetchone()

        if giv_data:
            await message.reply('Данный розыгрыш уже добавлен')
            return

        end_data = end_data + timedelta(hours=3)
        end_time = end_data.strftime('%H:%M')
        end_date = end_data.strftime('%Y-%m-%d')

        winner_count = message.giveaway.winner_count
        country_codes = message.giveaway.country_codes

        if not country_codes:
            country_codes = ' '
        else:
            country_codes = str(country_codes)

        month_count = message.giveaway.premium_subscription_month_count

        added_date = (message.date + timedelta(hours=3)).strftime('%Y-%m-%d')

        channels_count = len(message.giveaway.chats)
        
        if not month_count:
            mess = await bot.forward_message(config.STARS_CHAT, chat_id, message.message_id)
            giveaway_link = f'https://t.me/tg_freebies_stars/{mess.message_id}'
            stars_count = message.giveaway.prize_star_count
            if not add_giveaway('stars', special_key, country_codes, stars_count, winner_count, None,
                         end_date, end_time, giveaway_link, user_id, added_date, channels_count):
                return
        else:
            mess = await bot.forward_message(config.SUBS_CHAT, chat_id, message.message_id)
            giveaway_link = f'https://t.me/tg_freebies_premium/{mess.message_id}'
            if not add_giveaway('premium', special_key, country_codes, None, winner_count, month_count, end_date,
                         end_time, giveaway_link, user_id, added_date, channels_count):
                return
            
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        user_balance = cursor.fetchone()[0]

        reward = random.randint(1, 3)
        cursor.execute("INSERT INTO transactions (id, type, amount) VALUES (?, ?, ?)", (user_id, "giveaway", reward))
        
        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (user_balance + reward, user_id))
        database.commit
        today_date = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d')
        tomorrow_date = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=1)).strftime('%Y-%m-%d')
        cursor.execute('SELECT folder_link FROM folders WHERE folder_date = ?', (today_date,))
        today_folder = cursor.fetchone()
        cursor.execute('SELECT folder_link FROM folders WHERE folder_date = ?', (tomorrow_date,))
        tomorrow_folder = cursor.fetchone()

    msk_now = (datetime.now(pytz.timezone("Europe/Moscow")))
    tomorrow_msk = (msk_now + timedelta(days=1)).strftime("%Y-%m-%d")
    msk_now = msk_now.strftime("%Y-%m-%d")
    if tomorrow_folder:
        if end_date == tomorrow_msk:
            await bot.send_message(FOLDER_MANAGER_ID, "На завтра был добавлен новый розыгрыш! Уважаемый менеджер, обновите папку")
    if today_folder:
        if end_date == msk_now:
            await bot.send_message(FOLDER_MANAGER_ID, "На сегодня был добавлен новый розыгрыш! Уважаемый менеджер, обновите папку")

    addedgiv_text = '<b>Розыгрыш был добавлен, спасибо :)</b>'
    await message.reply(addedgiv_text, parse_mode='HTML')
