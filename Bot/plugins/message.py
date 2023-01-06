import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from Bot import bot, dp
from Bot.helper.writeToImage import create_card
from config import base_url


class UserChoiceState(StatesGroup):
    template = State()
    sender_name = State()
    receiver_name = State()


url = base_url + "api/templates"

response = requests.request("GET", url)
images = response.json()['data']


@dp.message_handler(commands="start")
async def start_handler(message: types.Message):
    text = "🎉 Welcome to the Holiday Card Generator Bot! 🎉" \
           "\n\nThis bot helps you create personalized holiday cards with custom names and templates. " \
           "To get started, click the [Create Card] button and follow the prompts."
    button = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    ).add(KeyboardButton("✨ Create Card ✨"))
    await message.answer(text, reply_markup=button)


@dp.message_handler(Text(equals="✨ Create Card ✨"))
async def create_card_handler(message: types.Message):
    text = "🎊🎉🎊🎉🎊🎉\n\nPlease select a holiday:\n\n🎊🎉🎊🎉🎊🎉"
    button = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("🌼 አዲስ ዓመት 🌼", callback_data='holiday_none'),
        InlineKeyboardButton("✝️ መስቀል ✝️", callback_data='holiday_none'),
        InlineKeyboardButton("☪️ አረፋ ☪️", callback_data='holiday_none'),
        InlineKeyboardButton("🎄 ገና  🎅", callback_data='holiday_gena'),
        InlineKeyboardButton("🍋 ጥምቀት 🍋", callback_data='holiday_none'),
        InlineKeyboardButton("🌙 መውሊድ 🌙", callback_data='holiday_none'),
        InlineKeyboardButton("☦️ ፋሲካ ☦️", callback_data='holiday_none'),
        InlineKeyboardButton("🌼 አዲስ ዓመት 🌼", callback_data='holiday_none')
    )
    await message.answer(text, reply_markup=button)


@dp.callback_query_handler(Text(startswith='holiday'))
async def holiday_handler(message: types.CallbackQuery):
    if message.data == 'holiday_none':
        await message.answer("Currently not available", show_alert=True)
        return
    await card_templates(message, 0)
    await UserChoiceState.template.set()


@dp.callback_query_handler(Text(startswith='choose'), state=UserChoiceState.template)
async def template_pagination(query: types.CallbackQuery, state: FSMContext):
    if query.data.startswith('choose_back'):
        current = query.data.split("_")[-1]
        await card_templates(query, int(current))
    if query.data.startswith('choose_next'):
        current = query.data.split("_")[-1]
        await card_templates(query, int(current))
    if query.data.startswith('choose_select'):
        selected = int(query.data.split("_")[-1])
        await state.update_data({"template": images[selected]})
        await query.message.answer("Enter sender name")
        await UserChoiceState.next()


@dp.message_handler(state=UserChoiceState.sender_name)
async def sender_name_handler(message: types.Message, state: FSMContext):
    if len(message.text) > 25:
        await message.answer("Name too long :( \n\nuse less than 25 chars")
        return
    await state.update_data({"sender_name": message.text})
    await message.answer("Enter receiver name")
    await UserChoiceState.next()


@dp.message_handler(state=UserChoiceState.receiver_name)
async def receiver_name_handler(message: types.Message, state: FSMContext):
    if len(message.text) > 25:
        await message.answer("Name too long :( \n\nuse less than 25 chars")
        return
    await state.update_data({"receiver_name": message.text})
    data = await state.get_data()
    s = create_card(data)
    cap = f"""🎄 *Merry Christmas*, {data['receiver_name']}! 🎄

Wishing you a season filled with 🎁 *joy* 🎁, 💕 *love* 💕, and all your favorite things. 
Hope your holiday is as warm and wonderful as you are. 

🎅 *Your*, {data['sender_name']} 🎅"""

    button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Share", switch_inline_query="")
    )
    await message.answer_photo(types.InputFile(s), caption=cap, parse_mode="MARKDOWN", reply_markup=button)
    await state.finish()


async def card_templates(message, current=0):
    user_id = message.from_user.id
    await message.message.delete()
    text = "Choose template"
    button = InlineKeyboardMarkup()
    if current - 1 >= 0:
        button.insert(InlineKeyboardButton("⬅️", callback_data=f'choose_back_{current - 1}'))
    button.insert(
        InlineKeyboardButton("Select ✅", callback_data=f'choose_select_{current}'),
    )
    if current < len(images) - 1:
        button.insert(InlineKeyboardButton("➡️", callback_data=f'choose_next_{current + 1}'))
    await bot.send_photo(
        user_id,
        base_url + "api/template/" + images[current],
        caption=text,
        reply_markup=button
    )
