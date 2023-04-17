from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

weather_start_message = "🌡️ Погода"
news_start_message = "📰 Новости"
notes_start_message = "🍺 Заметки"


def GREET_KEYBOARD():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(weather_start_message)
    markup.add(news_start_message)
    markup.add(notes_start_message)

    return markup


def WEATHER_DATES():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("1", "2", "4")

    return markup
