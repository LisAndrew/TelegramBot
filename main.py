import json
import logging


import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor

from api.WeatherApi import getWeather
from states.WeatherState import WeatherState

from keyboards import GREET_KEYBOARD, weather_start_message, news_start_message, notes_start_message, WEATHER_DATES

import matplotlib.pyplot as plt

# x_values = ['1', '2', '3', '4', '5']
# y_values = [3, 10, 20, 8, 6]
#
# # Строим график
# plt.plot(x_values, y_values, color='black')
#
# # Добавляем заголовок и метки осей
# plt.title("Динамика температуры")
# plt.xlabel("temp °C")
# plt.ylabel("Дни")
#
# # Сохраняем график в файл
# plt.savefig('my_plot.png')

logging.basicConfig(level=logging.INFO)

API_TOKEN = '5769100992:AAF7kcWJyc15w7Y32_JKK6LfbJ-Ew1-uexc'

bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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

        reply_markup = GREET_KEYBOARD(),
        parse_mode = ParseMode.MARKDOWN,
    )

@dp.message_handler(text=[weather_start_message, news_start_message, notes_start_message])
async def process_commands(message: types.Message):
    messageText = message.text;

    if message.text == weather_start_message:
        await WeatherState.city.set()
        await bot.send_message(message.chat.id, "Введите ваш город")

@dp.message_handler(state=WeatherState.city)
async def process_city(message: types.Message, state: FSMContext):
    messageText = message.text

    await state.update_data(city=messageText)
    await WeatherState.next()

    await message.reply("Количество дней для погоды?", reply_markup=WEATHER_DATES())

@dp.message_handler(lambda message: message.text.isdigit(), state=WeatherState.days)
async def process_city(message: types.Message, state: FSMContext):
    messageText = message.text
    await state.update_data(days=int(messageText))
    weatherInfo = await state.get_data()


    res = await getWeather(weatherInfo.get('city'))

    list = res['list'][0]

    mainStr = list['main']
    temp = mainStr['temp']
    feelsLike = mainStr['feels_like']

    weather = list['weather'][0]
    weatherDescription = weather['description']

    # TODO Сделать функцию по построеню графика
    # await bot.send_photo(
    #     message.chat.id,
    #     photo=open("my_plot.png", 'rb')
    # )

    await bot.send_message(
        message.chat.id,
        md.text(
            md.text(f"Температура в данный момент {temp}, но {weatherDescription}, поэтому ощущается как {feelsLike}"),
            sep='\n',
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(lambda message: not message.text.isdigit(), state=WeatherState.days)
async def process_days(message: types.Message):
    return await message.reply("Нужно ввести число, друг")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
