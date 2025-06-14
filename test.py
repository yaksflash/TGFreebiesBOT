'''from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from config import TOKEN
import sqlite3
import logging
from aiogram.types import CallbackQuery, ContentType
from aiogram import Router, F, types
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.content_type == ContentType.GIVEAWAY)
async def start_handler(message: types.Message):
    channels_count = len(message.giveaway.chats)
    print(channels_count)




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')'''


vadim_loh_code = '''а=int(input())
out=0
while a!=0:
   if a%3==0:
       out+=1
   a=int(input())
print(out)'''
for symbol in vadim_loh_code:
    if symbol in "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя":
        print("Vadim loh realno :)))")