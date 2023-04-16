from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

wheater_start_message = "🌡️ Погода"
news_start_message = "📰 Новости"
notes_start_message = "🍺 Заметки"


def GREET_KEYBOARD():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(wheater_start_message)
    markup.add(news_start_message)
    markup.add(notes_start_message)

    return markup
