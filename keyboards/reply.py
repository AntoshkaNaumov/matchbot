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
        ],
        [
            KeyboardButton(text="отправить донат")
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
