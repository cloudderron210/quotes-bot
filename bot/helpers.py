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
    times = set()

    while len(times) < num_times:
        hour = randint(0,23)
        minute = randint(0, 59)
        seconds = randint(0, 59)
        times.add(time(hour, minute, seconds))
        
    return sorted(list(times))



async def schedule_messages(chat_id: int, session: AsyncSession, num_messages: int | None = None, times: list | None = None) -> None:
    if not times and num_messages: 
        _times = generate_random_times(num_messages)
    elif times:
        _times = []
        for t in times:
            hour = int(t[0:2])
            minute = int(t[3:5])
            _times.append(time(hour,minute))
        
    for t in _times:
        trigger = CronTrigger(hour=t.hour, minute=t.minute, second=t.second)
        scheduler.add_job(
            func=periodic_message,
            trigger=trigger,
            args=[chat_id, session],
            id=f'{chat_id}_time_{t.hour}_{t.minute}_{t.second}'
        )
    

    


    
