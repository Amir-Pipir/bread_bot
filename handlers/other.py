import string
from aiogram import types, Dispatcher
from database import sql_file
from keyboards import kb_other, kb_other2, kb_other3, kb_other4
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from create_bot import bot
import random
import datetime

days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
Day = days[datetime.datetime.today().weekday()]


class Address(StatesGroup):
    add = State()


class NewAddress(StatesGroup):
    new_add = State()


class Order(StatesGroup):
    day = State()
    order = State()
    order_size = State()


# @dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет,это бот для заказов хлеба от Светланы!)")
    msg = await bot.send_message(message.chat.id, 'Если вы хотите отменить какое-то действие,напишите "отмена"\n\nЕсли есть вопросы звоните 89272444459 (Светлана) или 89375288443(Амир)')
    to_pin = msg.message_id
    await bot.pin_chat_message(chat_id=message.chat.id, message_id=to_pin)
    if await sql_file.start_db(message.from_user.id) == None:
        await message.answer(
            "Напишите свой адрес проживания(Поселок,улица,дом)\nЧтобы мы в будущем знали куда доставлять хлеб)")
        await Address.add.set()
    else:
        await message.answer(f"Здравствуйте,{message.from_user.first_name}!)", reply_markup=kb_other)


# @dp.message_handler(state= Address.add)
async def user_address(message: types.Message, state: FSMContext):
    address = message.text
    id = message.from_user.id
    username = message.from_user.username
    await sql_file.insert_user(id, username, address, 'user')
    await state.finish()
    await message.answer("Отлично,что будем дальше делать?", reply_markup=kb_other)


async def start_ordering(message: types.Message):
    await sql_file.check_address_db(message, message.from_user.id)


async def ordering(message: types.Message):
    await message.answer("На какой день вы хотите сделать заказ?", reply_markup=kb_other3)
    await Order.day.set()


async def order_day(message: types.Message, state: FSMContext):
    if message.text != Day:
        async with state.proxy() as data:
            data['day'] = message.text
        await Order.next()
        await message.answer("Выбирайте!", reply_markup=kb_other2)
    else:
        await message.answer("Хлеб на сегодня мы уже испекли😊\nЗакажите на другой день)", reply_markup=kb_other)
        await ordering(message)

async def order_bread(message: types.Message, state: FSMContext):
    if message.text == "Серый хлеб🍞" or message.text == "Хлеб с семечками🥜":
        async with state.proxy() as data:
            data['order'] = message.text
        async with state.proxy() as data:
            day = tuple(data.values())[0]
        x = await sql_file.check_order_size(day)
        await message.answer(f"На {day} мы можем испечь еще {12 - x} хлебов")
        await message.answer("Сколько вам нужно?(Напишите цифру)")
        await Order.next()
    else:
        await message.answer("У нас нет такого!", reply_markup=kb_other)
        await state.finish()


async def order_ins_day(message: types.Message, state: FSMContext):
    size = int(message.text)
    async with state.proxy() as data:
        day = tuple(data.values())[0]
        order_content = tuple(data.values())[1]
    x = await sql_file.check_order_size(day)
    order_id = ''.join(random.choice(string.digits) for i in range(8))
    if x + size > 12:
        await message.answer(f"К сожалению мы не можем сделать {size} хлеб(-а,-ов),вы можете заказать не больше {12 - x}")
        await state.finish()
        await message.answer("Заказ отменен!", reply_markup=kb_other)
    elif x + size <= 12:
        add = await sql_file.insert_order(message.from_user.id, day, order_content, size, 'неотдан', order_id)
        price = await sql_file.check_price(order_content)
        await state.finish()
        await message.answer("Ваш заказ принят!😁", reply_markup=kb_other)
        await message.answer(f"В {day}\nНаш курьер принесет {order_content} {size} шт по адресу {add}\nЦена заказа: {price*size} руб")


async def address_no(message: types.Message):
    await message.answer("Напишите новый адрес(Поселок,улица,дом)")
    await NewAddress.new_add.set()


async def new_address(message: types.Message, state: FSMContext):
    address = message.text
    await sql_file.update_add(message, message.from_user.id, address)
    await state.finish()
    await message.answer("Адрес доставки изменен", reply_markup=kb_other)


# @dp.message_handler(state="*", commands = "отмена")
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")


async def delete_ord(message: types.Message):
    orders = await sql_file.order_find(message.from_user.id)
    if len(orders) == 0:
        await message.answer("У вас нету заказов🙃")
    else:
        for x in orders:
            await message.answer(f"Заказ №{x[0]}\n{x[1]}\n{x[2]}\n{x[3]} шт", reply_markup=kb_other4)


async def delete_mes_ord(callback: types.CallbackQuery):
    res = callback.message.text.split()
    await sql_file.delete_order(res[1].replace("№", ""))
    await callback.message.delete()
    await callback.message.answer(f"*Заказ {res[1]} отменен*", reply_markup=kb_other)


async def main_menu(message: types.Message):
    x = await sql_file.check_menu()
    if len(x) != 0:
        for res in x:
            await message.answer(f"{res[0]}\n{res[1]}\nЦена: {res[2]} руб")
    else:
        await message.answer("Сейчас меню обновляется)\nБлагодарим за ожидание!☺️")


async def echo(message: types.Message):
    await message.answer(message.text)


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(user_address, state=Address.add)
    dp.register_message_handler(start_ordering, Text('Заказать'))
    dp.register_message_handler(delete_ord, Text('Отменить заказ'))
    dp.register_message_handler(main_menu, Text('Меню'))
    dp.register_callback_query_handler(delete_mes_ord, text='delete')
    dp.register_message_handler(address_no, text="Нет,поменяйте")
    dp.register_message_handler(ordering, text="Да,на этот")
    dp.register_message_handler(order_day, state=Order.day)
    dp.register_message_handler(order_bread, state=Order.order)
    dp.register_message_handler(order_ins_day, state=Order.order_size)
    dp.register_message_handler(new_address, state=NewAddress.new_add)
    dp.register_message_handler(echo)
