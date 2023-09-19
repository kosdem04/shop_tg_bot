from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import app.database.request as db


# Основные кнопки бота при команде /start
main_kb = [
    [KeyboardButton(text='Мои заказы'),
     KeyboardButton(text='Каталог')],
    [KeyboardButton(text='Корзина'),
     KeyboardButton(text='Контакты')],
    [KeyboardButton(text='Помощь'),
     KeyboardButton(text='Найти')],
]

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню.')

# Основные кнопки бота при команде /start для администратора
main_admin_kb = [
    [KeyboardButton(text='Каталог'),
     KeyboardButton(text='Корзина')],
    [KeyboardButton(text='Контакты'),
     KeyboardButton(text='Админ-панель')],
    [KeyboardButton(text='Найти'),
     KeyboardButton(text='Мои заказы')],
]

main_admin = ReplyKeyboardMarkup(keyboard=main_admin_kb,
                                 resize_keyboard=True,
                                 input_field_placeholder='Выберите пункт меню.')


# Основные кнопки бота админ-панели
admin_panel_kb = [
    [KeyboardButton(text='Добавить товар')],
    [KeyboardButton(text='Удалить товар')],
    [KeyboardButton(text='Сделать рассылку')],
    [KeyboardButton(text='Выйти')],
]

admin_panel = ReplyKeyboardMarkup(keyboard=admin_panel_kb,
                                  resize_keyboard=True,
                                  input_field_placeholder='Выберите пункт меню.')


add_kb = [
    [KeyboardButton(text='Отмена')],
]

add = ReplyKeyboardMarkup(keyboard=add_kb,
                                  resize_keyboard=True,
                                  input_field_placeholder='Выберите пункт меню.')


register_order_kb = [
    [InlineKeyboardButton(text='Оформить заказ', callback_data='register_order')]
]

register_order = InlineKeyboardMarkup(inline_keyboard=register_order_kb)


payment_order_kb = [
    [InlineKeyboardButton(text='Наличный', callback_data=f'cash_{1}')],
    [InlineKeyboardButton(text='Безналичный', callback_data=f'cash_{0}')]
]

payment_order = InlineKeyboardMarkup(inline_keyboard=payment_order_kb)


delivery_order_kb = [
    [InlineKeyboardButton(text='Самовывоз', callback_data=f'delivery_{1}')],
    [InlineKeyboardButton(text='Курьером', callback_data=f'delivery_{0}')]
]

delivery_order = InlineKeyboardMarkup(inline_keyboard=delivery_order_kb)


# Основные кнопки бота при просмотре каталога
def catalog():
    catalogs = db.show_catalog()
    # print(sneakers)
    items = InlineKeyboardBuilder()
    for sq in catalogs:
        items.row(InlineKeyboardButton(text=sq.type_name, callback_data=f'catalog_{sq.type_id}'))
    return items.adjust(2).as_markup()


#def delete_from_basket(product_id):
    #delete = db.delete_from_basket(product_id)
    # print(sneakers)
    #items = InlineKeyboardBuilder()
    #items = [[InlineKeyboardButton(text='Удалить из корзины', callback_data=str(product_id))]]
    #return items


def show_producer(id_type):
    producers = db.show_producer(id_type)
    # print(sneakers)
    items = InlineKeyboardBuilder()
    for sq in producers:
        items.row(InlineKeyboardButton(text=sq.producer_name, callback_data=sq.producer_name))
    items.row(InlineKeyboardButton(text='Назад', callback_data='producer_exit'))
    return items.adjust(2).as_markup()


def items_xiaomi():
    xiaomi = db.show_xiaomi('Xiaomi')
    # print(sneakers)
    items = InlineKeyboardBuilder()
    for sq in xiaomi:
        items.row(InlineKeyboardButton(text=sq.product_name, callback_data=f'product_{sq.product_id}'))
    items.row(InlineKeyboardButton(text='Назад', callback_data='phone_exit'))
    return items.adjust(2).as_markup()


def items_realme():
    realme = db.show_realme('Realme')
    # print(sneakers)
    items = InlineKeyboardBuilder()
    for sq in realme:
        items.row(InlineKeyboardButton(text=sq.product_name, callback_data=f'product_{sq.product_id}'))
    items.row(InlineKeyboardButton(text='Назад', callback_data='phone_exit'))
    return items.adjust(2).as_markup()


def items_huawei():
    huawei = db.show_huawei('Huawei')
    # print(sneakers)
    items = InlineKeyboardBuilder()
    for sq in huawei:
        items.row(InlineKeyboardButton(text=sq.product_name, callback_data=f'product_{sq.product_id}'))
    items.row(InlineKeyboardButton(text='Назад', callback_data='phone_exit'))
    return items.adjust(2).as_markup()


def add_to_basket(product_id):
    items = InlineKeyboardBuilder()
    items.row(InlineKeyboardButton(text='Добавить в корзину', callback_data=f'addtobasket_{product_id}'))
    return items.adjust(2).as_markup()


def del_from_basket(product_id):
    items = InlineKeyboardBuilder()
    items.row(InlineKeyboardButton(text='Удалить из корзины', callback_data=f'delfrombasket_{product_id}'))
    return items.adjust(2).as_markup()


def search(stroka):
    search = db.search(stroka)
    # print(sneakers)
    items = InlineKeyboardBuilder()
    for sq in search:
        items.row(InlineKeyboardButton(text=sq.product_name, callback_data=f'product_{sq.product_id}'))
    items.row(InlineKeyboardButton(text='Вернуться в главное меню', callback_data='search_exit'))
    return items.adjust(2).as_markup()


def basket(user_id):
    baskets = db.show_basket(user_id)
    # print(sneakers)
    items = InlineKeyboardBuilder()
    for sq in baskets:
        items.row(InlineKeyboardButton(text=f'{sq[4]}шт {sq[2]} руб - {sq[1]}', callback_data=f'product_{sq[3]}'))
    return items.adjust(1).as_markup()


def order(user_id):
    order = db.show_orders(user_id)
    # print(sneakers)
    items = InlineKeyboardBuilder()
    for sq in order:
        items.row(InlineKeyboardButton(text=f'Заказ №{sq[0]}', callback_data=f'order_{sq[0]}'))
    return items.adjust(1).as_markup()


