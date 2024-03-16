import asyncio
from aiogram import Bot, Dispatcher

import handlers
from dayvinchick.data.database import DataBase
from config_reader import config


async def main() -> None:
    bot = Bot(config.bot_token.get_secret_value())
    dp = Dispatcher()
    db_users = DataBase("users_base.db", "users")
    db_likes = DataBase("users_base.db", "likes")

    await db_users.create_table()
    await db_likes.create_table()

    dp.include_routers(
        handlers.start.router,
        handlers.view_profile.router,
        handlers.questionare.router,
        handlers.create_profile.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, db=db_users)


if __name__ == "__main__":
    asyncio.run(main())
