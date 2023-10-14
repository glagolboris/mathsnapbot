import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import asyncio
import base64
from parser import Parser
import text


class AioBot:
    def __init__(self, api_id):
        self.bot = Bot(api_id)
        self.builder = InlineKeyboardBuilder()
        button = InlineKeyboardButton(text='Помощь', callback_data='help')
        self.builder.add(button)
        self.dispatcher = Dispatcher()
        self.run_sync_func()

    def handler_on_start(self):
        @self.dispatcher.message(CommandStart())
        async def handler_on_start(message: Message):
            await self.bot.send_photo(message.chat.id, photo=BufferedInputFile.from_file(path='photos/start.jpg', filename='start.jpg'), caption=text.start(), reply_markup=self.builder.as_markup())

    def handler_of_photo(self):
        @self.dispatcher.message(lambda m: m.photo)
        async def get_photo_with_equation(m: Message):
            photo = m.photo[-1]
            photo_id = await self.bot.get_file(photo.file_id)
            photo_in_bytes = await self.bot.download_file(photo_id.file_path)
            async with aiohttp.ClientSession() as session:
                parser = Parser(session, base64.b64encode(photo_in_bytes.read()))
                await self.bot.send_message(m.chat.id, f'ASCII код этого объекта: \n{await parser.get_equation}')
                answer = await parser.run_solve()
                await self.bot.send_message(m.chat.id, f'Решения этого объекта: \n {answer}')

        @self.dispatcher.message(Command('help'))
        async def get_help(message: Message):
            help_ = text.help()
            await self.bot.send_photo(message.chat.id, caption=help_, photo=BufferedInputFile.from_file('photos/help_photo.jpg', filename='help_photo.jpg'))

    def handler_callbacks(self):
        @self.dispatcher.callback_query(lambda call: call.data == 'help')
        async def callback(call: CallbackQuery):
            msg = self.bot.send_photo(call.message.chat.id, photo=BufferedInputFile.from_file('photos/help_photo.jpg', filename='help.jpg'), caption=text.help())
            await msg

    async def callback_of(self, msg):
        await self.bot.send_message(msg.message.chat.id, 'aboba')

    def run_sync_func(self):
        self.handler_on_start()
        self.handler_of_photo()
        self.handler_callbacks()

    async def start_polling(self):
        await self.dispatcher.start_polling(self.bot)


if __name__ == '__main__':
    aiobot = AioBot('6549930645:AAHfOD2NAvMZBHCT22BiZCOyRQBs9K4Cwzw')
    asyncio.run(aiobot.start_polling())
