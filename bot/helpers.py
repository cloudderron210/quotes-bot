from datetime import time
from random import randint


from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from bot.services.scheduler import scheduler 
from apscheduler.triggers.cron import CronTrigger
from bot.database import crud
from bot_instance import bot
from bot.layout import keyboards as kb

async def periodic_message(chat_id: int, session: AsyncSession):
    result = await crud.get_random_quote(chat_id, session)
    await bot.send_message(chat_id, f''' "{result}." \n \n © <b></b> ''', parse_mode='HTML', reply_markup=kb.turn_off) 

async def start_periodic_messages(chat_id, seconds: int, session: AsyncSession) -> None:
    scheduler.add_job(
        func=periodic_message,
        trigger=IntervalTrigger(seconds=seconds),
        args=[chat_id, session], 
        id=f"{chat_id}",
    ) 
    

def generate_random_times(num_times: int, send_at_nighttime: bool = True) -> list[time]:
    times = []

    for _ in range(num_times):
        hour = randint(0,23)
        minute = randint(0, 59)
        times.append(time(hour, minute))
        
    print(f'-------{times}')
    return sorted(times)



async def schedule_messages(chat_id: int, num_messages: int, session: AsyncSession) -> None:
    random_times = generate_random_times(num_messages)
    for t in random_times:
        trigger = CronTrigger(hour=t.hour, minute=t.minute)
        scheduler.add_job(
            func=periodic_message,
            trigger=trigger,
            args=[chat_id, session],
            id=f'{chat_id}_time_{t.hour}_{t.minute}'
        )




    
