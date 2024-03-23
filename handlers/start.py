from aiogram.types import Message
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram import types

from keyboards.reply import main
from data.database import DataBase

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Выберите действие:", reply_markup=main)


@router.message(F.text == "отправить донат")
async def send_donation(message: types.Message):
    await message.answer_photo(photo='AgACAgIAAxkBAAIFHmX-pxw5mF'
    'uA_UkpQ5jFZE3wN7qMAALY1jEbra_5S-GlUR0zMAfbAQADAgADeAADNAQ')
    await message.answer("Вы можете отправить донат на любую сумму на поддержание моего бота.")


@router.message(F.photo)
async def photo_handler(message: types.Message) -> None:
    photo_data = message.photo[-1]
    await message.answer(f'{photo_data}')
