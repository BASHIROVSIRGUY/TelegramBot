import os
import sys
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor
from models.answer_logic import AnswerChooser

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO, filename='./log/bot.log')

load_dotenv('./config/.env')
TOKEN = os.environ.get('TOKEN')

bot = Bot(token=TOKEN)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
dp = Dispatcher(bot=bot, loop=loop)
answer_obj = AnswerChooser(loop=loop)

if __name__ == '__main__':
    from controllers.handlers import dp, on_startup
    if len(sys.argv) > 1:
        if 'fill_db' in sys.argv:
            from fill_db import fill
            loop.run_until_complete(fill(answer_obj.db, "./вопросы-ответы.txt"))
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
