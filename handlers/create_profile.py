from typing import Generator

from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State

from keyboards.inline import inline_kb
from data.database import DataBase  # Импорт класса DataBase из файла database.py
from utils.states import Form


router = Router()

db = DataBase("users_base.db", "users")  # Создание экземпляра класса DataBase


@router.message(F.text == "2")
async def delete_profile(message: Message, db: DataBase) -> None:
    # Получаем имя пользователя из базы данных
    user_name = message.from_user.username
    if not user_name:
        await message.answer("Имя пользователя не найдено. Пожалуйста, установите username и повторите попытку.")
        return

    # Удаляем профиль пользователя по его имени пользователя
    await db.delete_user_data(user_name)
    await message.answer("Анкета успешно удалена.")


@router.message(F.text == "1")
async def view_profiles(message: types.Message, state: FSMContext):
    profiles = await db.get_all_profiles()  # Получаем все анкеты из базы данных
    if not profiles:
        await message.answer("В базе данных нет ни одной анкеты.")
        return

    # Создаем генератор, который будет возвращать по одной анкете
    profilegenerator = (profile for profile in profiles)

    # Получаем первую анкету
    profile = next(profilegenerator, None)

    # Если анкета есть, то отправляем ее пользователю
    if profile:
        await send_profile(message, profile, profilegenerator, state)  # Добавляем state в качестве аргумента
    else:
        await message.answer("В базе данных нет ни одной анкеты.")


@router.message(State(Form.name))
async def send_profile(message: types.Message, profile: tuple, profilegenerator: Generator, state: FSMContext):
    # Формируем текст анкеты
    profilemessage = f"Имя: {profile[2]}\n" \
                      f"Возраст: {profile[3]}\n" \
                      f"Город: {profile[4]}\n" \
                      f"Пол: {profile[5]}\n" \
                      f"О себе: {profile[7]}\n"

    # Отправляем текст анкеты
    await message.answer(profilemessage, reply_markup=inline_kb)

    # Отправляем фото
    await message.answer_photo(profile[9])  # profile[9] содержит photofileid из базы данных

    # Сохраняем текущую анкету и генератор в состояние
    await state.update_data(profile=profile, profilegenerator=profilegenerator)


@router.message(F.text.casefold())
async def my_profile(message: Message) -> None:
    if message.text == "моя анкета":
        #user_id = message.from_user.id
        user_name = message.from_user.username
        user_data = await db.get_user_data(user_name)

        if user_data:
            # Отправляем фото пользователю по photo_file_id
            await message.answer_photo(user_data['photo_file_id'], caption="Ваше фото")

            # Отправляем текст анкеты пользователю
            user_profile = f"Имя: {user_data['name']}\n" \
                           f"Возраст: {user_data['age']}\n" \
                           f"Город: {user_data['city']}\n" \
                           f"Пол: {user_data['sex']}\n" \
                           f"Предпочтения: {user_data['look_for']}\n" \
                           f"О себе: {user_data['about']}"
            # Формируем сообщение с анкетой пользователя и выбором действия
            reply_message = f"Ваша анкета:\n{user_profile}\n\nВыберите действие:\n" \
                            f"1. Смотреть анкеты.\n" \
                            f"2. Удалить анкету."
            #await message.answer(user_profile)
            await message.answer(reply_message)
        else:
            await message.answer("Ваша анкета не найдена.")
