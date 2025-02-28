from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.database.models import Author, Quote
from bot.states import AuthorState
from bot.layout import keyboards as kb
from bot.services.scheduler import scheduler 
from apscheduler.triggers.interval import IntervalTrigger 
from bot_instance import bot

router = Router()


class AddingQuote:
    @staticmethod
    @router.callback_query(F.data == "Add quote")
    async def add_quote_button(
        callback_query: CallbackQuery, state: FSMContext, session: AsyncSession
    ):
        current_author: Author = await crud.get_current_defualt_author(
            callback_query.message.chat.id, session
        )  # type:ignore
        await state.set_state(AuthorState.add_quote)
        await callback_query.message.edit_text(#type:ignore
            f"Enter new quote for {current_author.name}",
            reply_markup=kb.cancel_adding_new_quote,
        )  # type:ignore

    @staticmethod
    @router.message(F.text, AuthorState.add_quote)
    async def add_quote(message: Message, session: AsyncSession, state: FSMContext):
        current_author: Author = await crud.get_current_defualt_author(
            message.chat.id, session
        )  # type:ignore
        new_quote = await crud.add_quote(
            author=current_author, text=message.text, session=session #type:ignore
        )  

        await message.answer(f"{new_quote} has been added")
        await message.answer(
            f"Enter new quote for {current_author.name}",
            reply_markup=kb.cancel_adding_new_quote,
        )  # type:ignore

    @staticmethod
    @router.callback_query(F.data == "cancel_quote")
    async def cancel_add_quote(callback_query: CallbackQuery, state: FSMContext):
        await callback_query.answer()
        await callback_query.message.edit_text(#type:ignore
            "Menu", reply_markup=kb.build_menu(callback_query.message.chat.id)#type:ignore
        )  
        await state.clear()


class GettingRandomQuote:
    @staticmethod
    @router.callback_query(
        (F.data == "Get random quote") | (F.data == "one_more_quote")
    )
    async def get_random_quote(callback_query: CallbackQuery, session: AsyncSession):
        random_message = await crud.get_random_quote(
            callback_query.message.chat.id, session
        )
        await callback_query.answer()
        await callback_query.message.answer(
            f"""{random_message}. \n \n © <b></b> """, reply_markup=kb.one_more_quote
        )

    @staticmethod
    @router.callback_query(F.data == "Turn on")
    async def turn_on(callback_query: CallbackQuery, session: AsyncSession):
        await callback_query.message.answer( # type: ignore
            "Okey, let`s go...",
            reply_markup=kb.build_menu(callback_query.message.chat.id), #type: ignore
        )  # type:ignore
        # current_interval = get_interval_seconds( 
        #     callback_query.message.chat.id #type: ignore
        # )  
        scheduler.add_job(
            func=periodic_message,
            trigger=IntervalTrigger(seconds=5),
            args=[callback_query.message.chat.id, session], #type:ignore
            id="random_message",
        )  # type:ignore
            
    @staticmethod
    @router.callback_query(F.data == 'Turn off')
    async def turn_off(callback_query: CallbackQuery):
        await callback_query.message.edit_text("Turned off", reply_markup=kb.build_menu(callback_query.message.chat.id,change=True))  # type:ignore
        scheduler.remove_job(job_id='random_message')

        
class Settings:
    @staticmethod
    @router.callback_query(F.data == 'Settings')
    async def settings(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Settings', reply_markup=kb.settings) # type:ignore

    @staticmethod
    @router.callback_query(F.data == 'choose_mode')
    async def choose_mode(callback_query: CallbackQuery, session: AsyncSession):
        authors = await crud.get_all_authors_of_user(callback_query.message.chat.id, session)
        await callback_query.message.answer(f'{authors}')
        
        # await callback_query.answer()
        # await callback_query.message.edit_text('Choose mode', reply_markup=kb.choose_mode) #type:ignore
        
    @staticmethod
    @router.callback_query(F.data == 'back_to_menu')
    async def back_to_menu(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Menu', reply_markup=kb.build_menu(callback_query.message.chat.id)) # type:ignore
        
    @staticmethod 
    @router.callback_query(F.data == 'Choose author')
    async def choose_author(callback_query: CallbackQuery):
        current = crud.get_current_defualt_author(callback_query.message.chat.id) # type:ignore
        await callback_query.answer()
        await callback_query.message.edit_text(f'Choose author. Current: {current}', reply_markup=kb.build_authors(callback_query.message.chat.id)) # type:ignore
        
async def periodic_message(chat_id: int, session: AsyncSession):
    result = await crud.get_random_quote(chat_id, session)
    await bot.send_message(chat_id, f''' "{result}." \n \n © <b></b> ''', parse_mode='HTML', reply_markup=kb.turn_off) 
    
