import os
import asyncio
from io import BytesIO

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ContentType
from aiogram.filters import Command

from dotenv import load_dotenv

load_dotenv()

bot = Bot(os.environ["TG_TOKEN"])
db = Dispatcher()

user_data = {}

async def main():
    await db.start_polling(bot)


@db.message(Command("start"))
async def send_welcome(message: Message):
    # await message.reply(message.text)
    await message.reply("Welcome to Bear Marriage Bot! Use /upload to upload your data")


@db.message(Command("upload"))
async def upload_file(message: Message):
    await message.reply("Send attachment as txt file")

@db.message(lambda message: message.content_type == ContentType.DOCUMENT)
async def handle_docs(message: Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_content = await bot.download_file(file.file_path)

    user_data[message.from_user.id] = {
        "file": BytesIO(file_content.read()),
    }
    
    await message.reply("Data uploaded successfully!")

    button = [
        [InlineKeyboardButton(text="line", callback_data="method_line"),
        InlineKeyboardButton(text="hull", callback_data="method_hull"),
        InlineKeyboardButton(text="both", callback_data="method_both")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=button)
    await message.reply("Select method for building pairs:", reply_markup=keyboard)

if __name__ == "__main__":
    asyncio.run(main())
