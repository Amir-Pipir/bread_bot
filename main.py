from create_bot import dp
from aiogram.utils import executor
from handlers import admin,other


async def on_startup(_):
    print("Бот вышел в онлайн")

admin.register_handlers_admin(dp)
other.register_handlers_other(dp)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
