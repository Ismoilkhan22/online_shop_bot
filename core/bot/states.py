from aiogram.dispatcher.filters.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()

class CartStates(StatesGroup):
    select_product = State()
    select_color = State()

class LanguageStates(StatesGroup):
    select_language = State()