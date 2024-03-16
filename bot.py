import asyncio
from typing import Union
from contextlib import suppress
from aiogram import Router, Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode

from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase as MDB
from pymongo.errors import DuplicateKeyError

from callbacks import navigation, bank_loads_act

from keyboards.builders import inline_builder

#from middlewares.throlttling import ThrottlingMiddleware

from config_reader import config

router = Router()


@router.message(CommandStart())
@router.callback_query(F.data == "main_page")
async def start(message: Union[Message, CallbackQuery], db: MDB) -> None:
    with suppress(DuplicateKeyError):
        await db.users.insert_one(
            dict(
                _id=message.from_user.id,
                balance=500,
                bank={
                    "currency": [0, 0, 0],
                    "loans": {
                        "total_amount": 0,
                        "repaid": {"amount": 0, "when": []},
                        "when": {"start": "", "end": ""}
                    },
                    "deposit": {"total_amount": 0, "when": ""}
                },
                actives={"total_amount": 0, "items": []},
                passives={"total_amount": 0, "items": []},
                businesses={"total_amount": 0, "items": []}
            )
        )

    pattern = dict(
        text="Let's get down business!",
        reply_markup=inline_builder(
            texts=["Профиль", "Банк", "Рынки", "Бизнес"],
            callback_data=["profile", "bank", "markets", "business"],
            sizes=[2, 2]  # Укажите размеры рядов кнопок
        )
    )
    if isinstance(message, CallbackQuery):
        await message.message.edit_text(**pattern)
        await message.answer()
    else:
        await message.answer(**pattern)


@router.callback_query(F.data == "back")
async def back_to_main_page(query: CallbackQuery, db: MDB) -> None:
    await start(query, db)  # Переиспользуйте функцию start для возврата на главную страницу


async def main():
    bot = Bot(config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    cluster = AsyncIOMotorClient(host="localhost", port=27017)
    db = cluster.ecodb

    #dp.message.middleware(ThrottlingMiddleware())

    dp.include_routers(
        router,
        navigation.router,
        bank_loads_act.router

    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, db=db)


if __name__ == "__main__":
    asyncio.run(main())
