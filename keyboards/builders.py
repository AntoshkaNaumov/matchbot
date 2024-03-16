from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing import Union, List


def form_btn(text: Union[str, List]) -> ReplyKeyboardMarkup:
    if isinstance(text, str):
        text = [text]

    keyboard_buttons = [KeyboardButton(text=txt) for txt in text]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                   keyboard=[[button] for button in keyboard_buttons])

    return keyboard
