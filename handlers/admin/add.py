from loader import dp, db
from filters import IsAdmin
from handlers.user.menu import settings
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery
from states import CategoryState
from hashlib import md5
from aiogram.dispatcher import FSMContext

category_cb = CallbackData('category', 'id', 'action')


@dp.message_handler(IsAdmin(), text=settings)
async def process_settings(message: Message):

    markup = InlineKeyboardMarkup()

    for idx, title in db.fetchall('SELECT * FROM categories'):

        markup.add(InlineKeyboardButton(
            title, callback_data=category_cb.new(id=idx, action='view')))

    markup.add(InlineKeyboardButton(
        '+ Добавить категорию', callback_data='add_category'))

    await message.answer('Настройка категорий:', reply_markup=markup)

    @dp.callback_query_handler(IsAdmin(), text='add_category')
    async def add_category_callback_handler(query: CallbackQuery):
        await query.message.delete()
        await query.message.answer('Название категории?')
        await CategoryState.title.set()

        @dp.message_handler(IsAdmin(), state=CategoryState.title)
        async def set_category_title_handler(message: Message, state: FSMContext):
            category = message.text
            idx = md5(category.encode('utf-8')).hexdigest()
            db.query('INSERT INTO categories VALUES (?, ?)', (idx, category))

            await state.finish()
            await process_settings(message)