from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="моя анкета"),
            KeyboardButton(text="статистика"),
        ],
        [
            KeyboardButton(text="заполнить анкету"),
            KeyboardButton(text="просмотр анкет"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Создаем новое меню для статистики
stat_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="полученные лайки")],
        [KeyboardButton(text="отправленные лайки")],
        [KeyboardButton(text="назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

gender_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Парень"),
            KeyboardButton(text="Девушка"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

age_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="18-30 лет"),
            KeyboardButton(text="31-40 лет"),
        ],
        [
            KeyboardButton(text="41-50 лет"),
            KeyboardButton(text=">50 лет"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
