from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Написать", callback_data="write_message"),
            InlineKeyboardButton(text="Лайк", callback_data="like"),
            InlineKeyboardButton(text="Дизлайк", callback_data="dislike")
        ],
        [
            InlineKeyboardButton(text="В главное меню", callback_data="main_menu")
        ]
    ]
)
