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

from keyboards import GREET_KEYBOARD, weather_start_message, notes_start_message, WEATHER_DATES, \
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


@dp.message_handler(text=[weather_start_message, notes_start_message])
async def process_commands(message: types.Message):
    messageText = message.text

    if message.text == weather_start_message:
        await WeatherState.city.set()
        await bot.send_message(message.chat.id, "Введите ваш город", reply_markup=None)

    if message.text == notes_start_message:
        await NotesState.welcome.set()
        await message.reply("Выбери действие ", reply_markup=WELCOME_KEYBOARD_NOTES())


@dp.message_handler(state=WeatherState.city)
async def process_city(message: types.Message, state: FSMContext):
    messageText = message.text

    await state.update_data(city=messageText)
    await WeatherState.next()

    await message.reply("Количество дней для погоды?", reply_markup=WEATHER_DATES())


@dp.message_handler(lambda message: not message.text.isdigit(), state=WeatherState.days)
async def process_days(message: types.Message):
    return await message.reply("Нужно ввести число, друг",reply_markup=WEATHER_DATES())


@dp.message_handler(lambda message: int(message.text) not in [1,2,4], state=WeatherState.days)
async def process_city(message: types.Message):
    await message.reply("Пожалуйста, введи значения, равные 1 / 2 / 4", reply_markup=WEATHER_DATES())


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
            reply_markup=GREET_KEYBOARD(),
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
            photo=open("my_plot.png", 'rb'),
            reply_markup=GREET_KEYBOARD()
        )

    await state.finish()


@dp.message_handler(state=NotesState.welcome)
async def process_welcome(message: types.Message, state: FSMContext):
    if message.text == add_notes:
        await NotesState.add.set()
        await message.reply("Напиши текст заметки", reply_markup=None)
    
    if message.text == list_notes:
        data = await state.get_data()
        dataList = data.get('notesList')

        if (dataList == None):
            return await message.answer(
                md.text(
                    md.text("Заметки еще не созданы!"),
                    md.text("Ты что компьютер, что все помнишь? 🥸 "),
                    sep="\n"
                ),
                reply_markup=WELCOME_KEYBOARD_NOTES(),
                parse_mode=ParseMode.MARKDOWN,
        )

        await NotesState.list.set()
        await message.reply("Держи список заметок")

        currentNoteIndex = data.get('currentNoteIndex')
        note = dataList[0]
        builder = types.InlineKeyboardMarkup(row_width=3)


        if (currentNoteIndex != 0):
            note = dataList[currentNoteIndex]

            builder.insert(types.InlineKeyboardButton(
                text="<<",
                callback_data="prev_note",
                )
            )

        builder.insert(types.InlineKeyboardButton(
            text="Удалить заметку",
            callback_data="remove_note",
            )
        )

        if (len(dataList) > 1):
            builder.insert(types.InlineKeyboardButton(
                text=">>",
                callback_data="next_note",
                )
            )

        await message.answer(
                md.text(
                    md.text(
                        note),
                    sep='\n',
                ),
                reply_markup=builder,
                parse_mode=ParseMode.MARKDOWN,
        )

    

@dp.message_handler(state=NotesState.add)
async def process_add_notes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dataList = data.get('notesList')
    if dataList is None:
       dataList = []
    dataList.append(message.text)

    await state.update_data(notesList=dataList)
    await message.reply(f"Заметка добавлена '{message.text}'")
    await state.update_data(currentNoteIndex=0)
    await NotesState.welcome.set()

@dp.callback_query_handler(text="remove_note", state=NotesState.list)
async def handleNextNote(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    currentNoteIndex = data.get('currentNoteIndex')
    currentNotes = data.get('notesList')
    del currentNotes[currentNoteIndex]

    await state.update_data(notesList=currentNotes)

    await callback.message.answer("Удалено!")
    await state.update_data(currentNoteIndex=0)
    await NotesState.welcome.set()


@dp.callback_query_handler(text="next_note", state=NotesState.list)
async def handleNextNote(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    currentNoteIndex = data.get('currentNoteIndex')
    await state.update_data(currentNoteIndex=currentNoteIndex+1)
   
    data = await state.get_data()
    dataList = data.get('notesList')
    currentNoteIndex = data.get('currentNoteIndex')
    note = dataList[currentNoteIndex]

    builder = types.InlineKeyboardMarkup(row_width=4)

    if (currentNoteIndex != 0):
        builder.insert(types.InlineKeyboardButton(
            text="<<",
            callback_data="prev_note",
            )
        )

    builder.insert(types.InlineKeyboardButton(
        text="Удалить заметку",
        callback_data="remove_note",
        )
    )

    if (len(dataList) > 1 and currentNoteIndex != len(dataList) - 1):
        builder.insert(types.InlineKeyboardButton(
            text=">>",
            callback_data="next_note",
            )
        )


    await callback.message.edit_text(
            md.text(
                md.text(
                    note),
                sep='\n',
            ),
            reply_markup=builder,
            parse_mode=ParseMode.MARKDOWN,
    )

@dp.callback_query_handler(text="prev_note", state=NotesState.list)
async def handleNextNote(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    currentNoteIndex = data.get('currentNoteIndex')
    await state.update_data(currentNoteIndex=currentNoteIndex-1)
   
    data = await state.get_data()
    dataList = data.get('notesList')
    currentNoteIndex = data.get('currentNoteIndex')

    note = dataList[currentNoteIndex]

    builder = types.InlineKeyboardMarkup(row_width=4)

    if (currentNoteIndex != 0):
        builder.insert(types.InlineKeyboardButton(
            text="<<",
            callback_data="prev_note",
            )
        )

    builder.insert(types.InlineKeyboardButton(
        text="Удалить заметку",
        callback_data="remove_note",
        )
    )

    if (len(dataList) > 1 and currentNoteIndex != len(dataList) - 1):
        builder.insert(types.InlineKeyboardButton(
            text=">>",
            callback_data="next_note",
            )
        )


    await callback.message.edit_text(
            md.text(
                md.text(
                    note),
                sep='\n',
            ),
            reply_markup=builder,
            parse_mode=ParseMode.MARKDOWN,
    )



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
