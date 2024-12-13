import os
import asyncio
from io import BytesIO
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ContentType, CallbackQuery, FSInputFile
from aiogram.filters import Command

from dotenv import load_dotenv

from bear_marriage.data import read_points
from bear_marriage.find_pairs import connect_points
from bear_marriage.plotting_utils import plot_pairs_plotly

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


@db.callback_query(lambda c: c.data.startswith("method_"))
async def choose_method(callback_query: CallbackQuery):
    method_name = callback_query.data.split('_')[1]
    user_data[callback_query.from_user.id]["method"] = method_name
    user_data[callback_query.from_user.id]["build"] = True

    button = [[InlineKeyboardButton(text="build", callback_data="build")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=button)

    await callback_query.message.reply("Method selected! Ready to build", reply_markup=keyboard)
    await callback_query.answer()


@db.callback_query(lambda c: c.data == "build")
async def start_build(callback_query: CallbackQuery):
    await callback_query.message.reply("I started building..")
    
    user_id = callback_query.from_user.id
    file = user_data[user_id]["file"]
    method = user_data[user_id]["method"]

    points = read_points(file)
    method_list = []
    if method in ["both", "hull"]:
        method_list.append("hull")
    if method in ["both", "line"]:
        method_list.append("line")
    
    for meth in method_list:
        pairs = connect_points(points, method=meth)
        fig = plot_pairs_plotly(pairs)
    
        plot_path = Path("pairs_plot.png")
        fig.write_image(plot_path)

        await callback_query.message.reply_photo(FSInputFile(plot_path))

    await callback_query.answer()


if __name__ == "__main__":
    asyncio.run(main())
