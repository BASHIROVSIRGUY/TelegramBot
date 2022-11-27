import sys
import time
import random
import logging

import aiofiles
from aiogram.types import Message, CallbackQuery
from main import dp, answer_obj
from models.button_logic import ButtonCreator

preliminary_answers = [
    'Одну минуту, сейчас посмотрю',
    'Хороший вопрос, сейчас гляну в базе',
    'Минуточку, просмотрю архивы',
    'Действительно интересный вопрос, проверю в базе',
    'Хм, в базе данных что-то то такое было, скоро вернусь',
]


async def on_startup(_dp) -> None:
    logging.info(f"start up bot - {time.asctime()}")


@dp.message_handler(commands=['start'])
async def start_handler(message: Message) -> None:
    user_data = {
        'user_id': int(message.from_user.id),
        'username': message.from_user.username,
        'fullname': message.from_user.full_name
    }
    is_new_client = await remember_user(user_data)
    if is_new_client:
        answer_text = "Привет, "
    else:
        answer_text = "И снова здравствуй, "
    answer_text += f"{message.from_user.first_name}, напиши мне вопрос, а я постараюсь тебе ответить!"
    await message.answer(answer_text)


@dp.message_handler()
async def answer_handler(message: Message) -> None:
    rand_num_answer = int(random.random()*len(preliminary_answers))
    await message.answer(preliminary_answers[rand_num_answer])
    # start = time.time()
    answer = await get_answer(question=message.text)
    # await message.answer(text="Время выполения - {time}".format(time=time.time()-start))
    if answer is not None:
        await message.reply(answer)
    elif len(answer_obj.potential_question_from_db_dict) != 0:
        keyboard = await get_potential_keyboard()
        await message.answer("Может быть, интересует один из этих вопросов:", reply_markup=keyboard)
    else:
        await message.answer("К сожалению, не нашёл ответа на этот вопрос") # здесь возможно запоминание вопроса в базу и подключение оператора
    logging.info(f"{message.from_user.username}: {message.text} - {time.asctime()}")


@dp.callback_query_handler()
async def send_answer_inline(call: CallbackQuery):
    answer = await answer_obj.find_answer_by_id(call.data)
    await call.message.answer(answer)


async def get_answer(question: str) -> str:
    return await answer_obj.get_answer(question)


async def remember_user(user_data: dict) -> bool:
    if await answer_obj.db.check_user_by_id(user_data['user_id']):
        is_new_client = False
    else:
        is_new_client = True
        await answer_obj.db.add_user({
            'user_id': int(user_data['user_id']),
            'username': str(user_data['username']),
            'fullname': str(user_data['fullname'])
        })
    return is_new_client


async def get_potential_keyboard():
    buttons_obj = await answer_obj.loop.run_in_executor(
        None,
        ButtonCreator,
        answer_obj.potential_question_from_db_dict
    )
    return await buttons_obj.get_keyboard()
