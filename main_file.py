import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
        self.builder2 = InlineKeyboardBuilder()
        button_yes = InlineKeyboardButton(text='Да', callback_data='recognize_yes')
        button_no = InlineKeyboardButton(text='Нет', callback_data='recognize_no')
        self.builder2.add(button_yes, button_no)
        self.copies_parser: dict = {}

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
                await self.bot.send_message(m.chat.id, f'Выражение было распознано как: \n```{await parser.get_equation}```\. '
                                                       f'\nВерно?', reply_markup=self.builder2.as_markup(), parse_mode="MarkdownV2")
                self.copies_parser[m.chat.id] = parser

        @self.dispatcher.message(Command('help'))
        async def get_help(message: Message):
            help_ = text.help()
            await self.bot.send_photo(message.chat.id, caption=help_, photo=BufferedInputFile.from_file('photos/help_photo.jpg', filename='help_photo.jpg'))

    def handler_callbacks(self):
        @self.dispatcher.callback_query(lambda call: call.data == 'help')
        async def callback(call: CallbackQuery):
            msg = self.bot.send_photo(call.message.chat.id, photo=BufferedInputFile.from_file('photos/help_photo.jpg', filename='help.jpg'), caption=text.help())
            await msg

        @self.dispatcher.callback_query(lambda call: call.data == 'recognize_yes')
        async def callback_(call: CallbackQuery):
            await self.bot.send_message(call.message.chat.id, await self.copies_parser[call.message.chat.id].run_solve())

    def run_sync_func(self):
        self.handler_on_start()
        self.handler_of_photo()
        self.handler_callbacks()

    async def start_polling(self):
        await self.dispatcher.start_polling(self.bot)


if __name__ == '__main__':
    aiobot = AioBot('6698419785:AAHmb5ABGn1JNr0EG7zdRIfUMl-mPiCwBu8')
    asyncio.run(aiobot.start_polling())
