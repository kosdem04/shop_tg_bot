from aiogram import Router, types, F
from aiogram.filters import Command
import app.keyboards as kb
import app.database.request as db
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


router = Router()
geolocator = Nominatim(user_agent='shop_tg_bot')


class AddBasket(StatesGroup):
    user_id = State()
    product_id = State()
    value = State()


class Search(StatesGroup):
    text = State()


class Order(StatesGroup):
    user_id = State()
    payment = State()
    delivery = State()
    pointaddress = State()
    address = State()
    sum = State()


@router.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(AddBasket.user_id)
    await state.update_data(user_id=message.from_user.id)
    db.add_new_user(message.from_user.id, message.from_user.first_name)
    await message.answer(f'🖐 Привет 🖐\n Добро пожаловать в магазин электроники!',
                         reply_markup=kb.main)


@router.message(F.text == 'Каталог')
async def catalog(message: types.Message, state: FSMContext):
    await state.set_state(AddBasket.user_id)
    await state.update_data(user_id=message.from_user.id)
    await message.answer('👇 Каталог с товарами магазина 👇', reply_markup=kb.catalog())


@router.message(F.text == 'Мои заказы')
async def orders(message: types.Message):
    sq = db.is_order(message.from_user.id)
    if sq:
        await message.answer('👇 Мои заказы 👇', reply_markup=kb.order(message.from_user.id))
    else:
        await message.answer('У вас нет заказов')


@router.callback_query(F.data.startswith('order_'))
async def phones(callback: types.CallbackQuery):
    await callback.answer('Детали заказа')
    id_order = callback.data.split('_')[1]
    sq = db.show_order(id_order)
    result = "{:,}".format(sq.order_sum).replace(",", " ")
    await callback.message.answer(f'<b>Детали заказа № {sq.order_id}</b>')
    if sq.pointissue_address == 'нет':
        await callback.message.answer(text=f'<b>Товары:</b>\n {sq.order_value}\n'
                                           f'<b>Сумма:</b> {result} руб\n'
                                           f'<b>Способ оплаты:</b> {sq.order_payment}\n'
                                      f'<b>Способ доставки:</b> {sq.order_delivery}\n'
                                           f'<b>Адрес доставки:</b> {sq.order_address}\n'
                                      f'<b>Статус:</b> {sq.order_status}\n')
    else:
        await callback.message.answer(text=f'<b>Товары:</b>\n {sq.order_value}\n'
                                           f'<b>Сумма:</b> {result} руб\n'
                                           f'<b>Способ оплаты:</b> {sq.order_payment}\n'
                                           f'<b>Способ доставки:</b> {sq.order_delivery}\n'
                                           f'<b>Пункт выдачи:</b> {sq.pointissue_address}\n'
                                           f'<b>Статус:</b> {sq.order_status}\n')


@router.callback_query(F.data == 'search_exit')
async def search_exit(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer('Главное меню')
    await callback.message.answer('Главное меню', reply_markup=kb.main)


@router.message(F.text == 'Корзина')
async def basket(message: types.Message, state: FSMContext):
    sum = 0
    sq = db.show_basket(message.from_user.id)
    if sq == []:
        await message.answer('Ваша корзина пуста 🙃')
    else:
        await message.answer('Ваша корзина 🛒', reply_markup=kb.basket(message.from_user.id))
        for row in sq:
            sum = sum+row[2]*row[4]
        await message.answer('<b>‼️ Внимание ‼️\nДля изменения количества определённого товара необходимо удалить его из корзины и '
                             'снова добавить в корзину с нужным количеством</b>')
        result = "{:,}".format(sum).replace(",", " ")
        await message.answer(f'Итоговая сумма: {result} руб', reply_markup=kb.register_order)
        await state.set_state(Order.sum)
        await state.update_data(sum=sum)
        await state.set_state(Order.user_id)


@router.callback_query(F.data == 'register_order', Order.user_id)
async def register_order(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(user_id=callback.from_user.id)
    await state.set_state(Order.payment)
    await callback.answer('Выберите способ оплаты')
    await callback.message.edit_text('Способы оплаты:', reply_markup=kb.payment_order)


@router.callback_query(F.data.startswith('cash_'), Order.payment)
async def payment(callback: types.CallbackQuery, state: FSMContext):
    id_cash = callback.data.split('_')[1]
    if id_cash == '1':
        await state.update_data(payment='Наличный')
    else:
        await state.update_data(payment='Безналичный')
    await state.set_state(Order.delivery)
    await callback.answer('Выберите способ доставки')
    await callback.message.edit_text('Способы доставки:', reply_markup=kb.delivery_order)


@router.callback_query(F.data.startswith('delivery_'), Order.delivery)
async def delivery(callback: types.CallbackQuery, state: FSMContext):
    id_delivery = callback.data.split('_')[1]
    if id_delivery == '1':
        await state.update_data(delivery='Самовывоз')
        await state.set_state(Order.pointaddress)
        await callback.answer('Выберите пункт выдачи')
        await callback.message.edit_text('Пункты выдачи:', reply_markup=kb.show_pointissue())
    else:
        await state.update_data(delivery='Курьером')
        await state.set_state(Order.address)
        await callback.answer('Отправьте свои геоданные')
        await callback.message.answer('<b>Доставка курьером осуществляется только по г.Новосибирску в '
                                      'радиусе 10 км.</b>')
        await callback.message.answer('<b>Введите адрес в формате: улица, номер дома, Новосибирск, Россия </b>')


@router.message(Order.address)
async def delivery_address(message: types.Message, state: FSMContext):
    address = message.text
    location = geolocator.geocode(address)
    if location is None:
        await message.reply("Не удалось найти указанный адрес.", reply_markup=kb.main)
    latitude = location.latitude
    longitude = location.longitude

    # Координаты пользователя
    user_coordinates = (latitude, longitude)
    location = geolocator.reverse(f"{latitude}, {longitude}", timeout=10)
    address = location.address
    point_coordinates = (55.036896, 82.919244)
    distance = round(geodesic(user_coordinates, point_coordinates).kilometers, 0)
    if distance <= 10:
        await state.update_data(address=address)
        data = await state.get_data()
        db.add_order(data['user_id'], data['payment'], data['delivery'], data['sum'], data['address'])
        await message.answer('Зака оформлен')
        await message.answer('Заказ оформлен. Для просмотра детальной '
                             'информации о заказе перейдите в раздел "Мои заказы"', reply_markup=kb.main)
    else:
        await message.answer('Невозможно доставить заказ по заданному адресу.\n '
                             'Оформите заказ снова и выберите "Способ доставки: Самовывоз".',
                             reply_markup=kb.main)


@router.callback_query(F.data.startswith('pointissue_'), Order.pointaddress)
async def delivery_pointissue(callback: types.CallbackQuery, state: FSMContext):
    id_point = callback.data.split('_')[1]
    point = db.show_pointissues(id_point)
    await state.update_data(pointaddress=point)
    data = await state.get_data()
    db.add_order_point(data['user_id'], data['payment'], data['delivery'], data['sum'], data['pointaddress'])
    await callback.answer('Зака оформлен')
    await callback.message.answer('Заказ оформлен. Для просмотра детальной '
                                  'информации о заказе перейдите в раздел "Мои заказы"', reply_markup=kb.main)


@router.callback_query(F.data.startswith('catalog_'))
async def show_types(callback: types.CallbackQuery):
    id_type = callback.data.split('_')[1]
    await callback.answer('Производители')
    await callback.message.edit_text('👇 Производители 👇', reply_markup=kb.show_producer(id_type))


@router.callback_query(F.data == 'producer_exit')
async def produc(callback: types.CallbackQuery):
    await callback.message.edit_text('👇 Каталог с товарами магазина 👇', reply_markup=kb.catalog())


@router.callback_query(F.data.startswith('producer_'))
async def show_product(callback: types.CallbackQuery):
    id_producer = callback.data.split('_')[1]
    await callback.answer('Товары')
    await callback.message.edit_text('👇 Товары 👇', reply_markup=kb.items_product(id_producer))


@router.callback_query(F.data.startswith('exit_'))
async def xiaom(callback: types.CallbackQuery):
    id_types = callback.data.split('_')[1]
    await callback.answer('Производители')
    await callback.message.edit_text('👇 Производители 👇', reply_markup=kb.show_producer(id_types))


@router.callback_query(F.data.startswith('product_'))
async def item_desc(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddBasket.product_id)
    id_product = callback.data.split('_')[1]
    await state.update_data(product_id=id_product)
    await state.set_state(AddBasket.value)
    sq = db.show_phone_item(id_product)
    tp = db.show_types(sq.producer_id)
    await callback.answer(f'Название: {sq.product_name}')
    basket = db.is_basket(callback.from_user.id, id_product)
    if not basket:
        await callback.message.answer_photo(photo=sq.product_image,
                                            caption=f'<b>Название:</b>\n {sq.product_name}\n'
                                                    f'<b>Описание:</b>\n {sq.product_desc}\n'
                                                    f'<b>Цена:</b>\n {sq.product_price} руб',
                                            reply_markup=kb.del_from_basket(id_product))
        await callback.message.answer('Каталог:', reply_markup=kb.show_producer(tp))
    else:
        await callback.message.answer_photo(photo=sq.product_image,
                                            caption=f'<b>Название:</b>\n {sq.product_name}\n'
                                                    f'<b>Описание:</b>\n {sq.product_desc}\n'
                                                    f'<b>Цена:</b>\n {sq.product_price} руб',
                                            reply_markup=kb.add_to_basket(id_product))
        await callback.message.answer('Каталог:', reply_markup=kb.show_producer(tp))



@router.callback_query(F.data.startswith('delfrombasket_'))
async def del_from_basket(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(f'Удалить из корзины')
    id_product = callback.data.split('_')[1]
    sq = db.del_basket(callback.from_user.id, id_product)
    if sq == False:
        await callback.message.answer('При удалении возникла ошибка')
    else:
        await callback.message.answer('Товар удалён из корзины', reply_markup=kb.main)
        sum = 0
        sq = db.show_basket(callback.from_user.id)
        if sq == []:
            await callback.message.answer('Ваша корзина пуста 🙃')
        else:
            await callback.message.answer('Ваша корзина', reply_markup=kb.basket(callback.from_user.id))
            for row in sq:
                sum = sum+row[2]*row[4]
            await callback.message.answer('<b>Для изменения количества определённого товара '
                                          'необходимо удалить его из корзины и '
                                          'снова добавить в корзину с нужным количеством</b>')
            result = "{:,}".format(sum).replace(",", " ")
            await callback.message.answer(f'Итоговая сумма: {result} руб', reply_markup=kb.register_order)
            await state.set_state(Order.sum)
            await state.update_data(sum=sum)
            await state.set_state(Order.user_id)


# -----------------------------------------------------------------------------------------------------
@router.message(F.text == 'Контакты')
async def contacts(message: types.Message):
    await message.answer('Наши контакты: @kosdem04')


# -----------------------------------------------------------------------------------------------------
@router.message(F.text == 'Помощь')
async def helping(message: types.Message):
    await message.answer('В случае возникновения проблем свяжитесь с'
                         ' нашим оператором @kosdem04')


@router.callback_query(F.data.startswith('addtobasket_'))
async def add_value_basket(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddBasket.value)
    await callback.answer('Введите количество товара')
    await callback.message.answer('Введите количество товара. Максимальное количество 5 штук')


@router.message(AddBasket.value)
async def add_to_basket(message: types.Message, state: FSMContext):
    numbers = ('1', '2', '3', '4', '5')
    if (message.text.isdigit()) and (message.text in numbers):
        await state.update_data(value=message.text)
        data = await state.get_data()
        sq = db.add_basket(data['user_id'], data['product_id'], data['value'])
        if sq == False:
            await message.answer('Этот товар уже лежит в вашей корзине!\n'
                                 'Для изменения количества товара зайдите в корзину:)')
        else:
            await message.answer('Товар добавлен в корзину', reply_markup=kb.main)
    else:
        await message.answer('Вы ввели некорректное значение')


@router.message(F.text == 'Найти')
async def catalog(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(Search.text)
    await message.answer('Введите значение')


@router.message(Search.text)
async def catalog(message: types.Message):
    search = db.search(message.text)
    for sq in search:
        await message.answer('Результаты поиска', reply_markup=kb.search(message.text))
        break
    else:
        await message.answer('По вашему запросу ничего не найдено!', reply_markup=kb.not_search())
