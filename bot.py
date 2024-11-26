import asyncio
import logging
import os
from io import BytesIO
from time import perf_counter
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message, ContentType, CallbackQuery, FSInputFile, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from bear_marriage.data import read_points
from bear_marriage.find_pairs import connect_points
from bear_marriage.plotting_utils import plot_pairs_plotly, plot_distances
from dotenv import load_dotenv

load_dotenv()

# config tg app
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ["TG_TOKEN"])
dp = Dispatcher()
user_data = {}

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.reply("Welcome to the Bear Marriage Bot! Use /upload to upload your data.")

@dp.message(Command("upload"))
async def upload_file(message: Message):
    await message.reply("Send attachment in txt format.")

@dp.message(lambda message: message.content_type == ContentType.DOCUMENT)
async def handle_docs(message: Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_content = await bot.download_file(file.file_path)

    user_data[message.from_user.id] = {
        'file': BytesIO(file_content.read()),
        'method': None,
        'build': False
    }

    await message.reply("Data uploaded successfully!")

    buttons = [
        [InlineKeyboardButton(text="line", callback_data="method_line")],
        [InlineKeyboardButton(text="hull", callback_data="method_hull")],
        [InlineKeyboardButton(text="both", callback_data="method_both")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.reply("Select method for merrying bears:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("method_"))
async def set_method(callback_query: CallbackQuery):
    method = callback_query.data.split("_")[1]
    user_data[callback_query.from_user.id]['method'] = method
    user_data[callback_query.from_user.id]['build'] = True

    build_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Build", callback_data="build")]])
    await callback_query.message.reply("Method selected. Use the button below to build connections.", reply_markup=build_button)
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "build")
async def start_build(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id in user_data and user_data[user_id]['build']:
        file = user_data[user_id]['file']
        method = user_data[user_id]['method']

        points = read_points(file)
        methods = []
        hull = method in ["both", "hull"]
        line = method in ["both", "line"]
        if hull:
            methods.append("hull")
        if line:
            methods.append("line")

        for meth in methods:
            await callback_query.message.answer(f"Method: {meth}")
            await callback_query.message.answer("Building connections...")
            begin = perf_counter()
            pairs = connect_points(points, method=meth)
            end = perf_counter()

            await callback_query.message.answer(f"Build in {end-begin:.2f} seconds")
            await callback_query.message.answer("Plotting...")

            plot_pairs = plot_pairs_plotly(pairs)
            pairs_path = Path("pairs_plot.png")
            plot_pairs.write_image(pairs_path)
            photo = FSInputFile(pairs_path)
            await callback_query.message.answer_photo(photo)
            pairs_path.unlink()

            chart, statistics = plot_distances(pairs)
            distances_path = Path("distances_plot.png")
            chart.write_image(distances_path)
            photo = FSInputFile(distances_path)
            await callback_query.message.answer_photo(photo)
            distances_path.unlink()

            await callback_query.message.answer(f"Statistics: {statistics}")
    else:
        await callback_query.message.reply("Please upload a file and select a method first.")
    await callback_query.answer()

if __name__ == '__main__':
    asyncio.run(main())
