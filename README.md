## Holiday Card Generator Bot

- This is a Python bot that uses the **aiogram** library to help users create personalized holiday cards with custom names and templates. The bot allows users to choose a holiday, select a template, enter a sender name and a receiver name, and generate a card with the customizations.

## Requirements
- Python 3.7 or higher
- aiogram
- Pillow
## Usage
- To use the bot, send the `/start` command to start the conversation. You will be prompted to choose a holiday and a template, enter a sender name and a receiver name, and generate a card with the customizations. The generated card will be sent back to you as an image file.

## Customization
- You can customize the bot by adding or removing holidays and templates, or by modifying the text and emoji characters in the messages. You can also customize the card generation process by modifying the `create_card` function in the `Bot.helper.writeToImage` module.