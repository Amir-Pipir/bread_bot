from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

kb_admin = ReplyKeyboardMarkup(resize_keyboard=True)
kb_admin.add("Редактировать Меню", "Меню").add('Доставить заказы', 'Печь хлеб')

kb_admin1 = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
kb_admin1.add("Добавить Новое", "Редактировать Старое")

Button_kb = InlineKeyboardButton(text="Удалить", callback_data="delete_menu")
kb_admin2 = InlineKeyboardMarkup().add(Button_kb)

Button_kb1 = InlineKeyboardButton(text="Доставил", callback_data="deliver")
kb_admin3 = InlineKeyboardMarkup().add(Button_kb1)

kb_admin4 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_admin4.add("На завтра", "На сегодня")