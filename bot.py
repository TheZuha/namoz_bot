import asyncio
import logging
import sys
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import CallbackQuery, ParseMode
from apis import get_prayer_times, get_today_prayer_times
from db import save_user_to_db, get_db_pool
from keyboards import city_keyboard, month_keyboard, day_keyboard

TOKEN = "7499964348:AAHULQjhVIJ4HuXAhJiVZpIzOYYnWAsFVpc"
logging.basicConfig(level=logging.INFO)

user_data = {}

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

ADMIN_ID = '846986401'


async def on_start(message: types.Message, pool):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    await save_user_to_db(pool, user_id, full_name, username)
    await message.reply(
        f"Assalomu Alaykum! 👋\n\n"
        f"Hurmatli {message.from_user.full_name} (@{message.from_user.username})!\n\n"
        f"Botdan foydalanish uchun quyidagi komandalarni ishlating:\n"
        f"/namoz - Namoz vaqtlarini bilish\n"
        f"/today - Bugungi namoz vaqtlarini ko‘rish (Toshkent sh.)"
    )


async def send_message_to_users(pool, message_text):
    async with pool.acquire() as conn:
        users = await conn.fetch('SELECT * FROM users')
        for user in users:
            try:
                await bot.send_message(user['user_id'], message_text)
            except Exception as e:
                print(f"Xatolik: {e}")


async def send_image_to_users(pool, image_path):
    async with pool.acquire() as conn:
        users = await conn.fetch('SELECT * FROM users')
        for user in users:
            try:
                with open(image_path, 'rb') as image_file:
                    await bot.send_photo(user['user_id'], photo=image_file)
            except Exception as e:
                print(f"Xatolik: {e}")


async def start_bot():
    async with get_db_pool() as pool:
        # Start komandasi uchun xususiy handler
        @dp.message_handler(commands=['start'])
        async def start(message: types.Message):
            await on_start(message, pool)

        # Admin paneli
        @dp.message_handler(commands=['admin'])
        async def admin_panel(message: types.Message):
            if str(message.from_user.id) == ADMIN_ID:
                await message.reply(
                    "Admin paneliga xush kelibsiz!\n\n"
                    "Foydalanuvchilarni ko'rish uchun /users ni yozing.\n"
                )

        # Foydalanuvchilarni ko'rsatish
        @dp.message_handler(commands=['users'])
        async def show_users(message: types.Message):
            if str(message.from_user.id) == ADMIN_ID:
                async with pool.acquire() as conn:
                    users = await conn.fetch('SELECT * FROM users')
                    users_list = '\n'.join(
                        [f"ID: {user['user_id']}\nIsm: {user['full_name']}\nUsername: @{user['username']}\n{'-' * 30}"
                         for user in users])
                    await message.reply(
                        f"Foydalanuvchilar:\n\n{users_list if users_list else 'Hech qanday foydalanuvchi mavjud emas.'}")

        # Xabar yuborish
        @dp.message_handler(commands=['send_message'])
        async def send_message(message: types.Message):
            if str(message.from_user.id) == ADMIN_ID:
                message_text = "Foydalanuvchilarga yuboriladigan xabar"
                await send_message_to_users(pool, message_text)
                await message.reply("Xabar foydalanuvchilarga yuborildi.")


        # Namoz vaqtlarini ko'rsatish
        @dp.message_handler(commands=['today'])
        async def today(message: types.Message):
            user_id = message.from_user.id
            city = 'Toshkent'
            today = datetime.date.today()
            month = str(today.month)
            day = str(today.day)
            prayer_times = get_prayer_times(city, month, day)
            await message.reply(prayer_times)

        # Shaharni tanlash
        @dp.message_handler(commands=['namoz'])
        async def namoz(message: types.Message):
            await message.reply("Shaharni tanlang🏙️:", reply_markup=city_keyboard())

        # Shahar, oy, kun uchun callback handler
        @dp.callback_query_handler(lambda c: c.data and c.data.startswith('city:'))
        async def city_callback(callback_query: CallbackQuery):
            city = callback_query.data.split(':')[1]
            user_data[callback_query.from_user.id] = {'selected_city': city}
            await bot.edit_message_text("Oyni tanlang🌜:", chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id, reply_markup=month_keyboard())

        @dp.callback_query_handler(lambda c: c.data and c.data.startswith('month:'))
        async def month_callback(callback_query: CallbackQuery):
            month = callback_query.data.split(':')[1]
            user_data[callback_query.from_user.id]['month'] = month
            await bot.edit_message_text("Kunni tanlang☀️:", chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id, reply_markup=day_keyboard(month))

        @dp.callback_query_handler(lambda c: c.data and c.data.startswith('day:'))
        async def day_callback(callback_query: CallbackQuery):
            day = callback_query.data.split(':')[1]
            user_data[callback_query.from_user.id]['day'] = day
            city = user_data[callback_query.from_user.id]['selected_city']
            month = user_data[callback_query.from_user.id]['month']
            prayer_times = get_prayer_times(city, month, day)
            await bot.edit_message_text(prayer_times, chat_id=str(callback_query.from_user.id),
                                        message_id=callback_query.message.message_id)

        await dp.start_polling()


# Asinxron ishlarni bajarish
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(start_bot())
