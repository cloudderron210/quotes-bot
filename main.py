import asyncio
import logging

from aiogram import Dispatcher, types
from bot.middleware import DatabaseMiddleware
from bot_instance import bot
# from bot.handlers.user_handlers import user_router
# from bot.handlers.inline_handlers import inline_router
# from bot.handlers.callback_handlers import callback_router
from bot.config import BotConfig
from bot.services.scheduler import start_scheduler
from bot.handlers import router as root_router

dp = Dispatcher()

dp.update.middleware(DatabaseMiddleware())

def register_routers(dp: Dispatcher) -> None:
    dp.include_router(root_router)
    
async def on_startup():
    start_scheduler()

async def main_function() -> None:
    ''' Entry point '''

    config = BotConfig(
        admin_ids=[123412,12342],
        welcome_message='Okey, lets go!'
    )
    
    dp['config'] = config
    await on_startup()

    register_routers(dp)
    dp.message
    await bot.set_my_commands([
        types.BotCommand(command='/start', description='Start the bot'),
        types.BotCommand(command='/menu', description='menu!'),
    ])
    
    await dp.start_polling(bot)    
    


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main_function())
    
