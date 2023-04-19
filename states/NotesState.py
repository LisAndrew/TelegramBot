from aiogram.dispatcher.filters.state import StatesGroup, State

class NotesState(StatesGroup):
    welcome = State()
    add = State()
    delete = State()
    list = State()
    notesList = State()
