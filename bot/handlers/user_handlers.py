from aiogram.filters import Command
from aiogram import Router, F
from aiogram.types import Message
# from ..layout.keyboard import inline_keyboard 
from bot.layout import keyboard as kb
from bot.config import BotConfig
from bot.mysql_connection import  check_default_author, get_default_author, get_random_message, insert_new_user, set_default_author, set_user_authors, set_user_frequency
from bot.sql.sqlorm import check_default_author_2, insert_new_user_2
from scheduler import scheduler
from apscheduler.triggers.interval import IntervalTrigger
from bot_instance import bot


user_router = Router()

@user_router.message(Command(commands=['menu','start']))
async def menu(msg: Message,) -> None:
    user_id = msg.chat.id
    try:
        # result = insert_new_user_2(str(user_id), str(msg.chat.username))
        res_check = check_default_author_2(user_id)
        await msg.answer(f'{res_check}')
        if res_check == 0:
            result2 = set_default_author(user_id, 'Jason Statham 🧔')
            # await msg.answer(f'{result2}')
        result3 = set_user_authors(user_id)
        # await msg.answer(f'{result}')
        # await msg.answer(f'{result3}')
    except Exception as e:
        await msg.answer(f'{e}')
        # print(f'{e}')
    try:
        set_user_frequency(user_id) 
    except Exception as e:
        print(f'{e}')
    print(msg.chat.id, msg.chat.username)
    await msg.answer('Menu:', reply_markup=kb.build_menu(msg.chat.id))

# @user_router.message(Command('start'))
# async def cmd_start(msg: Message, config: BotConfig) -> None:
#     ''' Processes the `start` '''
#     await msg.reply(config.welcome_message, reply_markup=kb.build_menu(msg.chat.id))


# @user_router.message(~F.text.startswith('*'))
# async def store_mes(msg: Message):
#     user_id = msg.from_user.id # type:ignore
#     user = msg.from_user.username # type:ignore
#     message_to_store = msg.text# type:ignore
#     result = store_message(str(user_id), f'{user}', f'{message_to_store}')
#     await msg.answer(text=f'{result}')


async def periodic_message(chat_id: int):
    result = get_random_message(chat_id)
    await bot.send_message(chat_id, f'{result}, {chat_id}')

@user_router.message(F.text == '* Turn on *')
async def turn_on(msg: Message):
    await msg.answer("Okey, let`s go...", reply_markup=kb.reply_keyboard_off)
    scheduler.add_job(periodic_message, IntervalTrigger(seconds=3), args=[msg.chat.id], id='random_message')
    
    
@user_router.message(F.text == '* Turn off *')
async def turn_off(msg: Message):
    await msg.answer("Turning off...", reply_markup=kb.reply_keyboard_on)
    scheduler.remove_job(job_id='random_message')
    
@user_router.message(F.text == '* + 1 s *')
async def plus_one(msg: Message):
    job = scheduler.get_job('random_message')
    trigger = job.trigger.interval
    seconds = int(trigger.total_seconds())
    scheduler.modify_job(job_id='random_message', trigger=IntervalTrigger(seconds=seconds+5))
    await msg.answer('modified')
    
@user_router.message(F.text == '* - 1 s *')
async def minus_one(msg: Message):
    job = scheduler.get_job('random_message')
    trigger = job.trigger.interval
    seconds = int(trigger.total_seconds())
    
    if seconds - 5 > 0:
        scheduler.modify_job(job_id='random_message', trigger=IntervalTrigger(seconds=seconds-5))
        await msg.answer('modified')
    else:
        await msg.answer('Are you mad? Singularity is too dangerous')
    
@user_router.message(Command('random'))
async def random_message(msg: Message):
    scheduler.add_job(periodic_message, IntervalTrigger(seconds=3), args=[msg], id='random_message')

@user_router.message(Command('stop'))
async def stop_random(msg: Message):
    scheduler.remove_job(job_id='random_message')

    
    
# unrelated

# @user_router.message(Command('get_puh'))
# async def get_puh(message: Message):
#     await message.answer_photo(photo='https://sun9-68.userapi.com/impg/PfCuwHK8pTht_neG2uowSdDiyyLHsv63hCpbbg/gWco6i3_CDA.jpg?size=2560x1928&quality=95&sign=cd65958a4c7a4f726194c2a52a2b84c1&type=album', caption='это пух')
