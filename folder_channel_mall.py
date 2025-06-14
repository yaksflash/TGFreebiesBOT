from aiogram import Bot
from datetime import datetime, timedelta
import asyncio
import sqlite3
import pytz
from config import CHANNEL_ID
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode

async def send_banner_if_20(bot: Bot):
    while True:
        msk_now = (datetime.now(pytz.timezone("Europe/Moscow")))
        if (msk_now.hour == 20 and msk_now.minute == 0):
            with sqlite3.connect("database.db") as database:
                cursor = database.cursor()

                tomorrow_msk = (msk_now + timedelta(days=1)).strftime("%Y-%m-%d")
                msk_now = msk_now.strftime("%Y-%m-%d")
                cursor.execute("SELECT * FROM folders WHERE folder_date = ?", (tomorrow_msk,))
                folder_link = cursor.fetchall()[0][1][8:]
            
                cursor.execute('SELECT * FROM giveaways WHERE end_date = ?', (tomorrow_msk,))
                giveaways = cursor.fetchall()
        
                cursor.execute("SELECT * FROM giveaways WHERE end_date = ? AND is_in_folder = ?", (tomorrow_msk, True))
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

            difference = len(giveaways) - len(infolder_givwaways)
            if difference != 0:
                if difference % 10 == 1:
                    word = "розыгрыша"
                else:
                    word = "розыгрышей"
                string = f'\n\n❌ В папке нет {difference} {word}\n<i>Их можно посмотреть <a href="https://t.me/tg_freebies_bot">в нашем боте</a></i>'
            else:
                string = ""
            text = f'''
<b>Розыгрыши на {tomorrow_msk}:</b>
{folder_link}
➖➖➖➖➖➖➖➖➖

<b>💎 Premium:</b> {premium_gifts} шт (подписок: {premium_subs})
<b>⭐️ Stars:</b> {stars_gifts} шт (звёзд: {stars_count}){string}

<a href="https://telegra.ph/TG-Freebies--Kratkij-FAQ-05-13">❓ Что это такое? Читайте FAQ</a>
'''

            photo = FSInputFile("images/channel_folder_banner.jpg")
            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=text, parse_mode=ParseMode.HTML)
            await asyncio.sleep(100)
        else:
            await asyncio.sleep(30)