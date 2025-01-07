import asyncpg
from contextlib import asynccontextmanager


# PostgreSQL bilan aloqani yaratish
@asynccontextmanager
async def get_db_pool():
    pool = await asyncpg.create_pool(
        user='postgres',
        password='1234',
        database='namoz_bot',
        host='localhost'
    )
    try:
        yield pool
    finally:
        await pool.close()


# Foydalanuvchi ma'lumotlarini saqlash
async def save_user_to_db(pool, user_id, full_name, username):
    async with pool.acquire() as connection:
        await connection.execute('''
            INSERT INTO users(user_id, full_name, username)
            VALUES($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE
            SET full_name = $2, username = $3
        ''', user_id, full_name, username)


# Foydalanuvchilarga xabar yuborish
async def send_message_to_users(pool, bot, message_text):
    async with pool.acquire() as connection:
        # Foydalanuvchilarni olish
        users = await connection.fetch('SELECT user_id FROM users')
        for user in users:
            try:
                # Xabar yuborish
                await bot.send_message(user['user_id'], message_text)
            except Exception as e:
                print(f"Failed to send message to {user['user_id']}: {e}")
