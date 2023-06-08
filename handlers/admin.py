from aiogram import types, Dispatcher
from keyboards import kb_admin, kb_admin1, kb_admin2, kb_other, kb_admin3, kb_admin4
from database import sql_file
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import datetime
from handlers.other import Day

days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
Tomorrow = days[datetime.datetime.today().weekday() + 1]


class Menu(StatesGroup):
    name = State()
    description = State()
    price = State()


async def start_admin(message: types.Message):
    if await sql_file.check_admin_db(message.from_user.id) == True:
        await message.answer("Вы вошли, как админ!", reply_markup=kb_admin)
    else:
        await message.reply("Вы не админ!😠")


async def deliver_orders(message: types.Message):
    orders = await sql_file.order_deliver(Day)
    if len(orders) != 0:
        await message.answer('Заказы на сегодня')
        for x in orders:
            await message.answer(f"Заказ №{x[0]}\nАдрес:{x[1]}\n{x[2]}\n{x[3]} шт", reply_markup=kb_admin3)
    else:
        await message.answer("Заказов на сегодня нет")


async def delivered(callback: types.CallbackQuery):
    res = callback.message.text.split()
    await callback.message.edit_text(f"Заказ №{res[1]} доставлен")
    await sql_file.delete_order(res[1].replace("№", ""))


async def bake_bread(message: types.message):
    await message.answer("На какой день вы хотите испечь хлеб?", reply_markup=kb_admin4)


async def bake_for_day(message: types.Message):
    day = ""
    if message.text == "На завтра":
        day = Tomorrow
    elif message.text == "На сегодня":
        day = Day
    breads = await sql_file.bake_bread_sql(day)
    if breads[0] == 0 and breads[1] == 0:
        await message.answer(f"Заказов {message.text.lower()} нет,отдыхай)", reply_markup=kb_admin)
    else:
        await message.answer(f"Серый хлеб - {breads[0]}\nХлеб с семечками - {breads[1]}", reply_markup=kb_admin)


async def redact_menu(message: types.Message):
    if await sql_file.check_admin_db(message.from_user.id) == True:
        await message.reply("Как именно вы хотите редактироваь меню?", reply_markup=kb_admin1)


async def delete_menu(message: types.Message):
    if await sql_file.check_admin_db(message.from_user.id) == True:
        x = await sql_file.check_menu()
        if len(x) != 0:
            for res in x:
                await message.answer(f"{res[0]}\n{res[1]}\nЦена: {res[2]} руб", reply_markup=kb_admin2)
        else:
            await message.reply("Сначала добавь меню!")
    else:
        await message.reply("Вы не админ!😠")


async def delete_oid_menu(callback: types.CallbackQuery):
    res = callback.message.text.split('\n')
    await sql_file.delete_menu(res[0])
    await callback.message.delete()
    await callback.message.answer(f"*Удалено {res[0].rstrip()}*", reply_markup=kb_admin)


async def update_menu_name(message: types.Message):
    if await sql_file.check_admin_db(message.from_user.id) == True:
        await message.reply("Напишите название продукта!")
        await Menu.name.set()
    else:
        await message.reply("Вы не админ!😠")


async def update_menu_descrp(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.reply("Описание:")
    await Menu.next()


async def update_menu_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await message.reply("Цена:")
    await Menu.next()


async def update_menu(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = int(message.text)
    await sql_file.insert_menu(tuple(data.values())[0], tuple(data.values())[1], tuple(data.values())[2])
    await state.finish()
    await message.answer("Готово!", reply_markup=kb_admin)


async def state_cansel(message: types.Message, state: FSMContext):
    cur_state = state.get_state()
    if cur_state is None:
        return
    await state.finish()
    if await sql_file.check_admin_db(message.from_user.id) != True:
        await message.reply("Ok", reply_markup=kb_other)
    else:
        await message.reply("Ok", reply_markup=kb_admin)


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(start_admin, commands=['admin'])
    dp.register_message_handler(state_cansel, state="*", commands="отмена")
    dp.register_message_handler(state_cansel, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(redact_menu, Text('Редактировать Меню'))
    dp.register_message_handler(deliver_orders, Text('Доставить заказы'))
    dp.register_callback_query_handler(delivered, text='deliver')
    dp.register_message_handler(delete_menu, Text('Редактировать Старое'))
    dp.register_callback_query_handler(delete_oid_menu, text='delete_menu')
    dp.register_message_handler(update_menu_name, Text('Добавить Новое'))
    dp.register_message_handler(update_menu_descrp, state=Menu.name)
    dp.register_message_handler(update_menu_price, state=Menu.description)
    dp.register_message_handler(update_menu, state=Menu.price)
    dp.register_message_handler(bake_bread, Text('Печь хлеб'))
    dp.register_message_handler(bake_for_day, Text(startswith='На '))
