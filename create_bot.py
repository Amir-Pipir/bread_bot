from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

storage=MemoryStorage

bot = Bot(token=os.getenv('BOT_TOKEN'))

dp = Dispatcher(bot, storage=MemoryStorage())

DB_URI=os.getenv("DB_URI")