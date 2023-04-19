import datetime
import logging

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.utils import executor

from api.WeatherApi import getWeather
from entities.TempList import TempList
from states.NotesState import NotesState
from states.WeatherState import WeatherState

from keyboards import GREET_KEYBOARD, weather_start_message, news_start_message, notes_start_message, WEATHER_DATES, \
    WELCOME_KEYBOARD_NOTES, add_notes, list_notes

import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)

API_TOKEN = 'token'

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
                'Я могу сохранять твои заметки и ты точно не забудешь какое пиво тебя попросили купить на субботнюю вечеринку'),
                    '!'),

            md.text('🤟', md.bold('Функционал доступен по кнопкам ниже, поэтому не заблудишься'), '.',
                    md.bold('Удачи, друг'), '!'),

            sep='\n\n',
        ),

        reply_markup=GREET_KEYBOARD(),
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(text=[weather_start_message, news_start_message, notes_start_message])
async def process_commands(message: types.Message):
    messageText = message.text;

    if message.text == weather_start_message:
        await WeatherState.city.set()
        await bot.send_message(message.chat.id, "Введите ваш город")

    if message.text == notes_start_message:
        await NotesState.welcome.set()
        await message.reply("Выбери действие ", reply_markup=WELCOME_KEYBOARD_NOTES())


@dp.message_handler(state=WeatherState.city)
async def process_city(message: types.Message, state: FSMContext):
    messageText = message.text

    await state.update_data(city=messageText)
    await WeatherState.next()

    await message.reply("Количество дней для погоды?", reply_markup=WEATHER_DATES())


@dp.message_handler(state=NotesState.welcome)
async def process_welcome(message: types.Message, state: FSMContext):
    if message.text == add_notes:
        await NotesState.add.set()
        return await message.reply("Напиши заметки")
    if message.text == list_notes:
        await NotesState.list.set()
        return await message.reply("Держи список заметок")


@dp.message_handler(state=NotesState.add)
async def process_add_notes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dataList = data.get('notesList')
    if dataList is None:
       dataList = []
    dataList.append(message.text)

    await state.update_data(notesList=dataList)
    await message.reply(f"Заметка добавлена {message.text}")
    await NotesState.welcome.set()


@dp.message_handler(state=NotesState.list)
async def process_list_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dataList = data.get('notesList')
    await message.reply(f"Список всех заметок {dataList}")


@dp.message_handler(lambda message: message.text.isdigit(), state=WeatherState.days)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(days=int(message.text))

    weatherInfo = await state.get_data()

    res = await getWeather(weatherInfo.get('city'))

    tList = TempList(res['list'])

    if weatherInfo.get('days') == 1:
        date = tList.getFirstDate()

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text(
                    f"Температура в данный момент {date.temp}, но {date.description}, поэтому ощущается как {date.feelsLike}"),
                sep='\n',
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        datesList = None

        if weatherInfo.get('days') == 2:
            today = datetime.date.today()
            fromDate = today + datetime.timedelta(days=1)
            toDate = today + datetime.timedelta(days=2)
            datesList = tList.getRangeDates(fromDate, toDate)
        else:
            datesList = tList.omitTodayFromList()

        chartInfo = tList.plotData(datesList)

        ax = plt.axes()
        ax.set_xticklabels(chartInfo['labels'])
        plt.plot(chartInfo['x'], chartInfo['y'], color='black')

        plt.title("Динамика температуры")
        plt.xlabel("Дни")
        plt.ylabel("temp °C")

        plt.savefig('my_plot.png')

        await bot.send_photo(
            message.chat.id,
            photo=open("my_plot.png", 'rb')
        )


@dp.message_handler(lambda message: not message.text.isdigit(), state=WeatherState.days)
async def process_days(message: types.Message):
    return await message.reply("Нужно ввести число, друг")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
