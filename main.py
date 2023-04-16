import logging


import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor

from keyboards import GREET_KEYBOARD, wheater_start_message, news_start_message, notes_start_message


logging.basicConfig(level=logging.INFO)


API_TOKEN = '5769100992:AAFybrewiL8qE7qZHTkJ8USUXx8Twn-CYtI'

bot = Bot(token=API_TOKEN)
# For example use simple MemoryStorage for Dispatcher.

storage = MemoryStorage()
dp = Dispatcher(bot)


# States
# class Form(StatesGroup):
#     name = State()  # Will be represented in storage as 'Form:name'
#     age = State()  # Will be represented in storage as 'Form:age'
#     gender = State()  # Will be represented in storage as 'Form:gender'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    markup = types.ReplyKeyboardRemove()

    await bot.send_message(

        message.chat.id,

        md.text(

            md.text('👋 Привет!'),

            md.text(
                '😎 Я твой бот-помощник в повседневных делах.'),

            md.text('🌡️ Хочешь узнать погоду на сегодня или другой промежуток дней?', md.bold(
                'Просто укажи город и дни. Я посоветую тебе как одеться, чтобы не заболеть'), '!'),

            md.text('📰 Хочешь узнать что случилось в мире пока ты спал?', md.bold(
                'Я отправлю тебе свежие новости'), '!'),

            md.text('🍺 Постоянно забываешь что нужно купить в магазине?', md.bold(
                'Я могу сохранять твои заметки и ты точно не забудешь какое пиво тебя попросили купить на субботнюю вечеринку'), '!'),

            md.text('🤟', md.bold('Функционал доступен по кнопкам ниже, поэтому не заблудишься'), '.', md.bold('Удачи, друг'), '!'),

            sep='\n\n',

        ),

        reply_markup=GREET_KEYBOARD(),
        parse_mode=ParseMode.MARKDOWN,
    )

@dp.message_handler(commands=[wheater_start_message, news_start_message,notes_start_message])
async def process_commands(message: types.Message):
    print(message)
    return

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
