import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as fmt
import re
from VK_Users import Users
import Api_Request as vk
from typing import Optional


API_TOKEN = 'TOKEN'
logging.basicConfig(level=logging.INFO)


class RequestParams(StatesGroup):
    sex = State()
    town = State()
    age_from = State()
    age_to = State()
    menu = State()


def render(user_dict):
    f_name = f'{user_dict["first_name"]}'
    l_name = f'{user_dict["last_name"]}'
    domain = f'https://vk.com/{user_dict["domain"]}'
    name_link = f'<a href="{domain}">{f_name} {l_name}</a>\n'
    photo_400 = user_dict['photo_400_orig']
    text = ''
    for field in user_dict:
        if field in ['about', 'music', 'books', 'status', 'games', 'movies', 'tv', 'personal:political', 'personal:religion', 'personal:people_main', 'personal:life_main']:
            if user_dict.get(field):
                #print(field, ' ', user_dict[field])
                if type(user_dict[field]) != dict:
                    text = text + f'{field} : {replace_tags(str(user_dict[field]))}\n'
                else:
                    continue
    return name_link, photo_400, text


def replace_tags(string):
    if type(string) == str:
        if re.search('<', string):
            return re.sub('<', '&lt;', string)
        if re.search('>', string):
            return re.sub('>', '&gt;', string)
        else:
            return string
    else:
        return string


def get_sex_keyboard():
    buttons = [
        InlineKeyboardButton(text='Девушку', callback_data='1'),
        InlineKeyboardButton(text='Парня', callback_data='2')
        ]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(*buttons)
    return keyboard


def get_status_keyboard():
    buttons = [
        InlineKeyboardButton(text='не в браке', callback_data='1'),
        InlineKeyboardButton(text='встречается', callback_data='2'),
        InlineKeyboardButton(text='помолвлен(а)', callback_data='3'),
        InlineKeyboardButton(text='в браке', callback_data='4'),
        InlineKeyboardButton(text='гражданский брак', callback_data='8'),
        InlineKeyboardButton(text='влюблен(а)', callback_data='7'),
        InlineKeyboardButton(text='все сложно', callback_data='5'),
        InlineKeyboardButton(text='в активном поиске', callback_data='6')
        ]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(*buttons)
    return keyboard


def get_menu_keyboard():
    filters = InlineKeyboardButton(text='фильтры', callback_data='filters')
    load_next = InlineKeyboardButton(text='загрузить следущие 5', callback_data='next_5_users')
    new_search = InlineKeyboardButton(text='новый поиск', callback_data='1')

    keyboard = InlineKeyboardMarkup(row_width=2).add(filters, load_next)
    return keyboard


bot = Bot(token=API_TOKEN)


dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])#, state=None
async def start(message: types.Message):
    await RequestParams.sex.set()
    await message.answer("Кого ищем?", reply_markup=get_sex_keyboard())


@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(lambda message: message.text.lower() == 'cancel', state='*')
async def cancel_handler(message: types.Message, state: FSMContext, raw_state: Optional[str] = None):
    """
    Allow user to cancel any action
    """
    #if raw_state is None:
    #    return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Canceled.', reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(text=['2', '1'], state=RequestParams.sex)
async def sex(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(sex=call.data)
    print(f'selected sex: {call.data}')
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await bot.send_message(chat_id=call.from_user.id, text='введи город')
    await RequestParams.next()


@dp.message_handler(state=RequestParams.town)
async def city(message: types.Message, state: FSMContext):
    if message.text.lower() == 'москва':
        selected_city = 1
    if message.text.lower() == 'пермь':
        selected_city = 110
    if message.text.lower() == 'челябинск':
        selected_city = 158
    await state.update_data(city=selected_city)
    print(f'selected city: {selected_city}')
    await RequestParams.next()
    await bot.send_message(chat_id=message.from_user.id, text='возраст от')


@dp.message_handler(state=RequestParams.age_from)
async def age_from(message: types.Message, state: FSMContext):
    await state.update_data(age_from=message.text)
    print(f'selected age from: {message.text}')
    await bot.send_message(chat_id=message.from_user.id, text='возраст до')
    await RequestParams.next()


@dp.message_handler(state=RequestParams.age_to)
async def age_to(message: types.Message, state: FSMContext):
    await state.update_data(age_to=message.text)
    print(f'selected age to: {message.text}')
    await bot.send_message(chat_id=message.from_user.id, text='делаю запрос..')
    user_data = await state.get_data()
    print('user data before request: ', user_data)
    await state.update_data(users=Users(vk.make_request(int(user_data['sex']), int(user_data['city']), int(user_data['age_from']), int(user_data['age_to']))))
    user_data = await state.get_data()
    await bot.send_message(chat_id=message.from_user.id, text=f'получено: {len(user_data["users"].sorted_users)} пользователя',
                           reply_markup=get_menu_keyboard())
    await RequestParams.next()


@dp.callback_query_handler(text=['next_5_users'], state=RequestParams.menu)
async def next_5(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    for user in user_data['users'].get_next_5():
        name_domain, photo, text = render(user)
        await bot.send_message(chat_id=call.from_user.id, text=f'{fmt.hide_link(photo)}\n'
                                                               f'{name_domain}\n'
                                                               f'{text}', parse_mode=types.ParseMode.HTML)
    users_left = len(user_data['users'].sorted_users) - user_data['users'].last_user
    await state.update_data(users=user_data['users'])
    await bot.send_message(chat_id=call.from_user.id, text=f'осталось: {users_left} пользователей', reply_markup=get_menu_keyboard())
    await RequestParams.menu.set()


executor.start_polling(dp, skip_updates=True)



















#def replace_tags(string):
#    if re.search('<', string):
#        return re.sub('<', '&lt;', string)
#    if re.search('>', string):
#        return re.sub('>', '&gt;', string)
#    else:
#        return string