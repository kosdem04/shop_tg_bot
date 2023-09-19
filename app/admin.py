from aiogram import Router, types, F
from aiogram.filters import Filter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
import app.database.request as db

from config import ADMINS


class AdminProtect(Filter):
    def __init__(self):
        self.admins = ADMINS

    async def __call__(self, message: types.Message):
        return message.from_user.id in self.admins


admin = Router()


class AddItem(StatesGroup):
    producer_id = State()
    name = State()
    description = State()
    price = State()
    image = State()



@admin.message(AdminProtect(), F.text == 'Админ-панель')
async def admin_panel(message: types.Message):
    await message.answer('Вы открыли админ-панель', reply_markup=kb.admin_panel)


@admin.message(AdminProtect(), F.text == 'Выйти')
async def admin_cancel(message: types.Message):
    await message.answer('Главное меню', reply_markup=kb.main_admin)


@admin.message(AdminProtect(), F.text == 'Отмена')
async def admin_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Главное меню', reply_markup=kb.admin_panel)


# -----------------------------------------------------------------------------------------------------
@admin.message(AdminProtect(), F.text == 'Добавить товар')
async def add_item(message: types.Message, state: FSMContext):
    await state.set_state(AddItem.producer_id)
    await message.answer('Введите название производителя', reply_markup=kb.add)


@admin.message(AdminProtect(), AddItem.producer_id)
async def add_item_name(message: types.Message, state: FSMContext):
    exist = db.select_producer(message.text)
    if exist == False:
        await message.answer('Такого производителя нет в базе данных\n'
                             'Список всех производителей в базе данных:')
        producer = db.show_phone_producer()
        for sq in producer:
            await message.answer(f'{sq.producer_name}\n')
    else:
        await state.update_data(producer_id=exist)
        await state.set_state(AddItem.name)
        await message.answer('Введите название товара')


@admin.message(AdminProtect(), AddItem.name)
async def add_item_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddItem.description)
    await message.answer('Введите описание товара')


@admin.message(AdminProtect(), AddItem.description)
async def add_item_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddItem.price)
    await message.answer('Введите цену товара')


@admin.message(AdminProtect(), AddItem.price)
async def add_item_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AddItem.image)
    await message.answer('Отправьте фотографию товара')


@admin.message(AdminProtect(), AddItem.image)
async def add_item_image(message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo[0].file_id)
    data = await state.get_data()
    db.add_product(data['producer_id'],data['name'], data['description'], data['price'],  data['image'])
    await state.clear()
    await message.answer('Товар добавлен', reply_markup=kb.admin_panel)

