from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from database import sql_file



kb_other = ReplyKeyboardMarkup(resize_keyboard=True)

kb_other.add('Заказать', 'Отменить заказ').row('Меню')

kb_other1 = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
kb_other1.add('Да,на этот', 'Нет,поменяйте')

kb_other2 = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
kb_other2.add('Серый хлеб🍞', 'Хлеб с семечками🥜')

kb_other3 = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
kb_other3.add('Пн', 'Ср', 'Пт').add('Сб', 'Вс')

Button = InlineKeyboardButton(text="Отменить",callback_data="delete")
kb_other4 = InlineKeyboardMarkup().add(Button)