from aiogram import types
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from typing import Generator
from aiogram.fsm.state import State

from utils.states import Form
from data.database import DataBase
from keyboards.inline import inline_kb
from keyboards.reply import main, stat_menu, gender_menu, age_menu

from aiogram import Bot


from config_reader import config

import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = Router()
bot = Bot(config.bot_token.get_secret_value())

db = DataBase("users_base.db", "users")  # Создание экземпляра класса
db2 = DataBase("users_base.db", "likes")


#@router.message(F.text == "просмотр анкет")
#async def view_profiles(message: types.Message, state: FSMContext):
#    profiles = await db.get_all_profiles()  # Получаем все анкеты из базы данных
#    if not profiles:
#        await message.answer("В базе данных нет ни одной анкеты.")
#        return

    # Создаем генератор, который будет возвращать по одной анкете
#    profilegenerator = (profile for profile in profiles)

    # Получаем первую анкету
#    profile = next(profilegenerator, None)

    # Если анкета есть, то отправляем ее пользователю
#    if profile:
#        await send_profile(message, profile, profilegenerator, state)  # Добавляем state в качестве аргумента
#    else:
#        await message.answer("В базе данных нет ни одной анкеты.")


@router.message(F.text == "просмотр анкет")
async def view_profiles(message: types.Message, state: FSMContext):
    await message.answer("Выберите пол:", reply_markup=gender_menu)


@router.message(F.text == "Парень")
async def view_profiles_by_gender(message: types.Message, state: FSMContext):
    gender = message.text
    print(gender)
    profiles = await db.get_profiles_by_gender(gender)  # Замените эту строку вашим запросом к базе данных
    print(profiles)
    if not profiles:
        await message.answer(f"В базе данных нет анкет с полом '{gender}'.")
        return

    profilegenerator = (profile for profile in profiles)
    profile = next(profilegenerator, None)

    if profile:
        await send_profile(message, profile, profilegenerator, state)
    else:
        await message.answer(f"В базе данных нет анкет с полом '{gender}'.")


@router.message(F.text == "Девушка")
async def view_profiles_by_gender(message: types.Message, state: FSMContext):
    gender = message.text
    print(gender)
    profiles = await db.get_profiles_by_gender(gender)  # Замените эту строку вашим запросом к базе данных
    print(profiles)
    if not profiles:
        await message.answer(f"В базе данных нет анкет с полом '{gender}'.")
        return

    profilegenerator = (profile for profile in profiles)
    profile = next(profilegenerator, None)

    if profile:
        await send_profile(message, profile, profilegenerator, state)
    else:
        await message.answer(f"В базе данных нет анкет с полом '{gender}'.")


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


# Добавляем обработчик для кнопки "Статистика"
@router.message(F.text == "статистика")
async def show_stat_menu(message: types.Message):
    await message.answer("Выберите вид статистики:", reply_markup=stat_menu)


@router.message(F.text == "полученные лайки")
async def view_likes_stat(message: types.Message):
    user_name = message.from_user.username
    if user_name:
        user_data = await db.get_user_data(user_name)
        if user_data:
            await message.answer(f"Количество полученных лайков: {user_data['likes']}")
        else:
            await message.answer("Ошибка: Ваша анкета не найдена.")
    else:
        await message.answer("Ошибка: Не удалось получить информацию о вашем пользователе.")


@router.message(F.text == "отправленные лайки")
async def sent_likes_stat(message: types.Message, db: DataBase):
    sender_username = message.from_user.username
    if sender_username:
        likes = await db.get_sent_likes(sender_username)
        if likes:
            response = "Отправленные лайки:\n"
            for like in likes:
                receiver_username = like[0]
                receiver_user_name = like[1]
                response += f"- [{receiver_user_name}](t.me/{receiver_username})\n"
            await message.answer(response)
        else:
            await message.answer("У вас пока нет отправленных лайков.")
    else:
        await message.answer("Ошибка: Не удалось получить информацию о вашем пользователе.")


@router.message(F.text == "назад")
async def back_to_main_menu(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=main)  # Отправляем главное меню


@router.callback_query(F.data == "write_message")
async def write_message_callback(query: types.CallbackQuery, state: FSMContext, db: DataBase):
    await query.answer()  # Ответим на запрос, чтобы Telegram не считал его просроченным

    data = await state.get_data()
    profile = data.get("profile")

    if profile:
        user_name = profile[1]  # ID автора анкеты
        author_data = await db.get_author_by_name(user_name)  # Получаем данные об авторе анкеты
        if author_data:
            # Формируем URI для открытия чата с пользователем
            username = author_data['user_name']
            chat_uri = f"https://t.me/{username}"
            await query.message.answer(f"Откройте чат с автором анкеты по ссылке: {chat_uri}")
        else:
            await query.message.answer("Информация об авторе анкеты не найдена.")
    else:
        await query.message.answer("Информация об анкете не найдена.")


@router.callback_query(F.data == "like")
async def likecallback(query: types.CallbackQuery, state: FSMContext, db: DataBase):
    await query.answer()  # Ответим на запрос, чтобы Telegram не считал его просроченным
    # Получаем текущую анкету и генератор из состояния
    data = await state.get_data()
    profile = data.get("profile")
    profilegenerator = data.get("profilegenerator")
    # Увеличиваем количество лайков в базе данных для текущего профиля
    await db.increment_likes(profile[1])  # Предположим, что profile[1] содержит идентификатор пользователя
    # Добавляем запись о лайке в базу данных
    sender_username = query.from_user.username  # Используем имя пользователя, который поставил лайк
    receiver_username = profile[1]
    await db.insert_like(sender_username, receiver_username)
    # Отправляем сообщение пользователю, что он поставил лайк
    await query.message.answer(f"Вы поставили лайк {profile[2]}.")
    # Получаем следующую анкету из генератора
    profile = next(profilegenerator, None)
    # Если анкета есть, то отправляем ее пользователю
    if profile:
        await send_profile(query.message, profile, profilegenerator, state)
    else:
        await query.message.answer("Вы просмотрели все анкеты в базе данных.")


@router.callback_query(F.data == "dislike")
async def dislikecallback(query: types.CallbackQuery, state: FSMContext):
    await query.answer()  # Ответим на запрос, чтобы Telegram не считал его просроченным
    # Получаем текущую анкету и генератор из состояния
    data = await state.get_data()
    profile = data.get("profile")
    profilegenerator = data.get("profilegenerator")
    # Отправляем сообщение пользователю, что он поставил дизлайк
    await query.message.answer(f"Вы поставили дизлайк {profile[2]}.")
    # Получаем следующую анкету из генератора
    profile = next(profilegenerator, None)
    # Если анкета есть, то отправляем ее пользователю
    if profile:
        await send_profile(query.message, profile, profilegenerator, state)
    else:
        await query.message.answer("Вы просмотрели все анкеты в базе данных.")


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(query: types.CallbackQuery):
    await query.answer()  # Ответим на запрос, чтобы Telegram не считал его просроченным
    await query.message.answer("Выберите действие:", reply_markup=main)  # Отправляем главное меню
    await query.message.delete_reply_markup()  # Скрываем inline клавиатуру
