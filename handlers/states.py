from aiogram.fsm.state import State, StatesGroup

class ProductCreationState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_description = State()
    waiting_for_price = State()
