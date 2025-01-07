import calendar
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

cities = ['Toshkent', 'Samarqand', 'Buxoro', 'Namangan', 'Andijon', "Farg'ona", 'Navoiy', 'Qarshi', 'Xiva', 'Jizzax',
          'Guliston']
months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']


def generate_keyboard(options, callback_prefix, row_width=3):
    keyboard = InlineKeyboardMarkup()
    row = []
    for index, option in enumerate(options):
        row.append(InlineKeyboardButton(text=option, callback_data=f"{callback_prefix}:{option}"))
        if (index + 1) % row_width == 0:
            keyboard.row(*row)
            row = []
    if row:
        keyboard.row(*row)
    return keyboard


def city_keyboard():
    return generate_keyboard(cities, 'city', row_width=3)


def month_keyboard():
    return generate_keyboard(months, 'month', row_width=3)


# ✅ Kunlar sonini oyga qarab aniqlash funksiyasi
def day_keyboard(month, year=2025):
    days_in_month = calendar.monthrange(year, int(month))[1]  # Oyga qarab kunlar soni
    days = [str(i) for i in range(1, days_in_month + 1)]
    return generate_keyboard(days, 'day', row_width=3)
