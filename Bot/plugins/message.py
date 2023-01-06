import os
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from Bot import bot, dp
from Bot.helper.writeToImage import create_card
from config import base_url


# Create a states group for storing user input
class UserChoiceState(StatesGroup):
    template = State()  # template choice state
    sender_name = State()  # sender name state
    receiver_name = State()  # receiver name state


# API endpoint for templates
url = base_url + "api/templates"

# Make a GET request to the API endpoint
response = requests.request("GET", url)
# Get the templates data from the API response
images = response.json()['data']


# Start command handler
@dp.message_handler(commands="start")
async def start_handler(message: types.Message):
    # Welcome message
    text = "🎉 Welcome to the Holiday Card Generator Bot! 🎉" \
           "\n\nThis bot helps you create personalized holiday cards with custom names and templates. " \
           "To get started, click the [Create Card] button and follow the prompts."
    # Create a reply keyboard with a "Create Card" button
    button = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    ).add(KeyboardButton("✨ Create Card ✨"))
    # Send the welcome message and reply keyboard
    await message.answer(text, reply_markup=button)


@dp.message_handler(Text(equals="✨ Create Card ✨"))
async def create_card_handler(message: types.Message):
    # Request holiday selection
    text = "🎊🎉🎊🎉🎊🎉\n\nPlease select a holiday:\n\n🎊🎉🎊🎉🎊🎉"
    # Create an inline keyboard with holiday options
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


# Holiday selection handler
@dp.callback_query_handler(Text(startswith='holiday'))
async def holiday_handler(message: types.CallbackQuery):
    # If the holiday is not available, show an alert
    if message.data == 'holiday_none':
        await message.answer("Currently not available", show_alert=True)
        return
    # Show the template selection page
    await card_templates(message, 0)
    # Set the state to template choice
    await UserChoiceState.template.set()


# Template selection page handler
@dp.callback_query_handler(Text(startswith='choose'), state=UserChoiceState.template)
async def template_pagination(query: types.CallbackQuery, state: FSMContext):
    # If the user clicks the "previous" button
    if query.data.startswith('choose_back'):
        # Get the current page number from the button data
        current = query.data.split("_")[-1]
        # Show the previous page of templates
        await card_templates(query, int(current))
    # If the user clicks the "next" button
    if query.data.startswith('choose_next'):
        # Get the current page number from the button data
        current = query.data.split("_")[-1]
        # Show the next page of templates
        await card_templates(query, int(current))
    # If the user clicks a template selection button
    if query.data.startswith('choose_select'):
        # Get the selected template number from the button data
        selected = int(query.data.split("_")[-1])
        # Save the selected template
        await state.update_data(template=images[selected])
        # Request the sender name
        text = "Please enter the sender name:"
        # Show the sender name input form
        await query.message.answer(text)
        # Set the state to sender name
        await UserChoiceState.sender_name.set()


# Sender name input handler
@dp.message_handler(state=UserChoiceState.sender_name)
async def sender_name_handler(message: types.Message, state: FSMContext):
    # Save the sender name
    async with state.proxy() as data:
        data['sender_name'] = message.text
    # Request the receiver name
    text = "Please enter the receiver name:"
    # Show the receiver name input form
    await message.answer(text)
    # Set the state to receiver name
    await UserChoiceState.receiver_name.set()


# Receiver name input handler
@dp.message_handler(state=UserChoiceState.receiver_name)
async def receiver_name_handler(message: types.Message, state: FSMContext):
    # If the receiver name is too long, send an error message and return
    if len(message.text) > 25:
        await message.answer("Name too long :( \n\nuse less than 25 chars")
        return
    # Update the FSM context with the receiver name
    await state.update_data({"receiver_name": message.text})
    # Get the data stored in the FSM context
    data = await state.get_data()
    # Generate the card using the create_card function
    s = create_card(data, message.from_user.id)
    # Set the caption for the generated card
    cap = f"""🎄 *Merry Christmas*, {data['receiver_name']}! 🎄
    
Wishing you a season filled with 🎁 *joy* 🎁, 💕 *love* 💕, and all your favorite things. 
Hope your holiday is as warm and wonderful as you are. 

🎅 *Your*, {data['sender_name']} 🎅"""
    # Create an inline keyboard for sharing the card
    button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Share", switch_inline_query="")
    )
    # Send the generated card to the user
    await message.answer_photo(types.InputFile(s), caption=cap, parse_mode="MARKDOWN", reply_markup=button)
    # remove the image
    os.remove(s)
    # Reset the FSM context
    await state.finish()


# Function for showing the template selection page
async def card_templates(message, current=0):
    # Get the user's ID
    user_id = message.from_user.id
    # Delete the previous message
    await message.message.delete()
    # Set the caption for the template selection page
    text = "Choose template"
    # Create an inline keyboard for pagination and template selection
    button = InlineKeyboardMarkup()
    # If the current page is not the first page, add a "previous" button
    if current - 1 >= 0:
        button.insert(InlineKeyboardButton("⬅️", callback_data=f'choose_back_{current - 1}'))
    # Add a template selection button
    button.insert(
        InlineKeyboardButton("Select ✅", callback_data=f'choose_select_{current}'),
    )
    # If the current page is not the last page, add a "next" button
    if current < len(images) - 1:
        button.insert(InlineKeyboardButton("➡️", callback_data=f'choose_next_{current + 1}'))
    # Send the template image to the user
    await bot.send_photo(
        user_id,
        base_url + "api/template/" + images[current],
        caption=text,
        reply_markup=button
    )

