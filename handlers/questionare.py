import aiohttp
import re

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.builders import form_btn
from data.database import DataBase

from utils.states import Form
from utils.city import check_city
from keyboards.reply import main

router = Router()

db = DataBase("users_base.db", "users")  # Создание экземпляра класса DataBase


@router.message(F.text == "заполнить анкету")
async def my_form(message: Message, state: FSMContext):
    #user_id = message.from_user.id
    user_name = message.from_user.username
    user_data = await db.get_user_data(user_name)

    if user_data:
        await message.answer("Такой пользователь уже существует!")
        return
    await state.set_state(Form.name)
    await message.answer(
        "Отлично, введи своё имя",
        reply_markup=form_btn([message.from_user.first_name])
    )


@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    name = message.text.strip()

    # Проверяем, что имя состоит только из букв русского или латинского алфавита
    if re.match("^[a-zA-Zа-яА-Я]+$", name):
        await state.update_data(name=name)
        await state.set_state(Form.age)
        await message.answer("Теперь укажи свой возраст")
    else:
        await message.answer("Некорректный ввод! Имя должно содержать только буквы русского или латинского алфавита.")


@router.message(Form.age)
async def form_age(message: Message, state: FSMContext):
    age_str = message.text.strip()
    if age_str.isdigit():
        age = int(age_str)
        if 16 <= age <= 80:
            await state.update_data(age=age)
            await state.set_state(Form.city)
            await message.answer("Теперь укажи свой город")
        else:
            await message.answer("Возраст должен быть от 16 до 80 лет. Попробуй ещё раз!")
    else:
        await message.answer("Попробуй ещё раз! Возраст должен быть целым числом.")


@router.message(Form.city)
async def form_city(message: Message, state: FSMContext):
    city_name = message.text.strip()
    if await check_city(city_name):
        await state.update_data(city=city_name)
        await state.set_state(Form.sex)
        await message.answer(
            "Теперь давай определимся с полом",
            reply_markup=form_btn(["Парень", "Девушка"])
        )
    else:
        await message.answer("Указанный город не найден. Попробуйте ещё раз!")
        return


@router.message(Form.sex, F.text.casefold().in_(["парень", "девушка"]))
async def form_sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await state.set_state(Form.look_for)
    await message.answer(
        "Кого ты предпочитаешь искать?",
        reply_markup=form_btn(["Парни", "Девушки", "Мне все равно"])
    )


@router.message(Form.sex)
async def incorrect_form_sex(message: Message, state: FSMContext):
    await message.answer("Выбери один вариант!")


@router.message(
    Form.look_for,
    F.text.casefold().in_(["девушки", "парни", "мне все равно"])
)
async def form_look_for(message: Message, state: FSMContext):
    await state.update_data(look_for=message.text)
    await state.set_state(Form.about)
    await message.answer("Теперь расскажи о себе")


@router.message(Form.look_for)
async def incorrect_form_look_for(message: Message, state: FSMContext):
    await message.answer("Выбери один вариант!")


@router.message(Form.about)
async def form_about(message: Message, state: FSMContext):
    if len(message.text) < 5:
        await message.answer("Введи что-нибудь поинтересней")
    else:
        await state.update_data(about=message.text)
        await state.set_state(Form.photo)
        await message.answer("Теперь отправь свое фото")


@router.message(Form.photo, F.photo)
async def form_photo(message: Message, state: FSMContext, db: DataBase):
    photo_file_id = message.photo[-1].file_id
    file_info = await message.bot.get_file(photo_file_id)
    photo_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_info.file_path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(photo_url) as resp:
            photo_data = await resp.read()

    data = await state.get_data()
    #user_id = message.from_user.id
    username = message.from_user.username

    await state.clear()

    frm_text = []
    [frm_text.append(value) for _, value in data.items()]
    await db.insert(username, frm_text, photo_data, photo_file_id)
    #await db.insert(user_id, frm_text, photo_data)

    await message.answer_photo(photo_file_id, "\n".join(map(str, frm_text)))
    await message.answer("Выберите действие:", reply_markup=main)


@router.message(Form.photo, ~F.photo)
async def incorrect_form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь фото!")
