import psycopg2
from create_bot import DB_URI
from keyboards import kb_other1

conn = psycopg2.connect(DB_URI, sslmode="require")
cursor = conn.cursor()


async def check_admin_db(id: str):
    cursor.execute(f"SELECT role FROM public.users WHERE id='{id}'")
    res = cursor.fetchone()
    if res[0].rstrip() == 'admin':
        return True


async def start_db(id: str):
    cursor.execute(f"SELECT * FROM public.users WHERE id='{id}'")
    return cursor.fetchone()


async def insert_user(id: str, username: str, address: str, role: str):
    cursor.execute('INSERT INTO public.users (id,username,address,role) VALUES(%s,%s,%s,%s)',
                   (id, username, address, role))
    conn.commit()


async def check_address_db(message, id: str):
    cursor.execute(f"SELECT * FROM public.users WHERE id='{id}'")
    result = cursor.fetchone()
    await message.answer(f"Вы хотите сделать заказ на следующий адрес?\n{result[2]}", reply_markup=kb_other1)


async def update_add(message, id: str, address: str):
    cursor.execute(f"UPDATE public.users SET address='{address}' WHERE id='{id}'")
    conn.commit()
    await message.answer(f"Вы хотите сделать заказ на следующий адрес?\n{address}", reply_markup=kb_other1)


async def insert_order(id: str, day: str, order_content: str, size: int, status: str, order_id: str):
    cursor.execute(f"SELECT * FROM public.users WHERE id='{id}'")
    res = cursor.fetchone()
    address = res[2].rstrip()
    cursor.execute(
        'INSERT INTO public.orders (id,day,address,order_content,size,status,order_id) VALUES(%s,%s,%s,%s,%s,%s,%s)',
        (id, day, address, order_content, size, status, order_id))
    conn.commit()
    return address


async def check_order_size(day: str):
    cursor.execute(f"SELECT size FROM public.orders WHERE day='{day}' and status='неотдан'")
    size = cursor.fetchall()
    y = 0
    for x in size:
        y += x[0]
    return y


async def order_find(id: str):
    cursor.execute(f"SELECT order_id,day,order_content,size FROM public.orders WHERE id='{id}' and status='неотдан'")
    return cursor.fetchall()


async def delete_order(order_id):
    cursor.execute(f"DELETE FROM public.orders WHERE order_id='{order_id}'")
    conn.commit()


async def insert_menu(name: str, description: str, price: int):
    cursor.execute("INSERT INTO public.menu (name,description,price) VALUES(%s,%s,%s)", (name, description, price))
    conn.commit()


async def delete_menu(name: str):
    cursor.execute(f"DELETE FROM public.menu WHERE name='{name}'")
    conn.commit()


async def check_menu():
    cursor.execute(f"SELECT * FROM public.menu")
    return cursor.fetchall()


async def check_price(order_content: str):
    cursor.execute(f"SELECT price from public.menu WHERE name='{order_content}'")
    return cursor.fetchone()[0]


async def update_admin(id: str):
    cursor.execute(f"UPDATE public.users SET role='admin' WHERE id='{id}'")
    conn.commit()


async def order_deliver(day: str):
    cursor.execute(
        f"SELECT order_id,address,order_content,size FROM public.orders WHERE day='{day}' and status='неотдан'")
    return cursor.fetchall()


async def bake_bread_sql(day: str):
    cursor.execute(f"SELECT order_content,size FROM public.orders WHERE day='{day}'")
    x = 0
    y = 0
    for i in cursor.fetchall():
        if i[0].rstrip() == "Серый хлеб🍞":
            x += i[1]
        elif i[0].rstrip() == "Хлеб с семечками🥜":
            y += i[1]
    return (x, y)
