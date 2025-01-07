import requests
from datetime import date


# ✅ Oy va kun bo‘yicha namoz vaqtlarini olish
def get_prayer_times(city, month, day):
    try:
        response = requests.get(f'https://islomapi.uz/api/monthly?region={city}&month={month}')
        data = response.json()
        daily_data = data[int(day) - 1]

        prayer_times = (f"""
📅 Shahar: {city}
🗓️ Oy: {month}
📆 Kun: {day}

Fajr (Bomdod): {daily_data['times']['tong_saharlik']} 🌄
Dhuhr (Peshin): {daily_data['times']['peshin']} ☀️
Asr: {daily_data['times']['asr']} 🌇
Maghrib (Shom): {daily_data['times']['shom_iftor']} 🌆
Isha (Hufton): {daily_data['times']['hufton']} 🌃
        """)
        return prayer_times
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"


# ✅ Bugungi kun uchun namoz vaqtlarini olish
def get_today_prayer_times(city):
    try:
        # API dan ma'lumot olish
        response = requests.get(f'https://islomapi.uz/api/daily?region={city}')
        data = response.json()

        # Bugungi namoz vaqtlarini olish
        prayer_times = (f"""
📅 Shahar: {city}
🗓️ Bugungi kun:

Fajr(Bomdod): {data['times']['tong_saharlik']} 🌄
Dhuhr(Peshin): {data['times']['peshin']} ☀️
Asr: {data['times']['asr']} 🌇
Maghrib(Shom): {data['times']['shom_iftor']} 🌆
Isha(Hufton): {data['times']['hufton']} 🌃
        """)
        return prayer_times
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"
