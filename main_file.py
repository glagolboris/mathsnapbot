import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.types.input_file import InputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from io import BytesIO
import asyncio
import base64
from parser import Parser
import text
# TODO: STATE находится в ответе на запрос editor
#  OCR запрос на расшифровку фото


class AioBot:
    def __init__(self, api_id):
        self.bot = Bot(api_id)
        self.dispatcher = Dispatcher()
        self.run_sync_func()

    def handler_on_start(self):
        @self.dispatcher.message(CommandStart())
        async def handler_on_start(message: Message):
            await self.bot.send_photo(message.chat.id, photo=InputFile('/Users/egor/PycharmProjects/hakaton/photos/start.jpg'))

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
            await self.bot.send_photo(message.chat.id, caption=help_, photo='/Users/egor/PycharmProjects/hakaton/photos/help_photo.jpg')

    def handler_callbacks(self):
        @self.dispatcher.callback_query(lambda call: call.data == 'solve')
        async def callback(call: CallbackQuery):
            msg = self.bot.send_message(call.message.chat.id, 'Ok. You may send me the image with equation')
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
    aiobot = AioBot('6698419785:AAHmb5ABGn1JNr0EG7zdRIfUMl-mPiCwBu8')
    asyncio.run(aiobot.start_polling())
