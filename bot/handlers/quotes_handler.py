import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.database.models import Author, Quote
from bot.layout.callbacks import AuthorCallback, UnitsCallback
from bot.states import AuthorState, FrequencyState
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
        j


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
        await callback_query.answer()
        await callback_query.message.edit_text('Choose Mode:', reply_markup=kb.choose_mode) 
    
    class ChooseMode:
        ''' MIXED '''
        @staticmethod
        @router.callback_query(F.data == 'mixed_au')
        async def mixed(callback_query: CallbackQuery):
            pass
            
        ''' CHOOSE AUTHOR'''
        @staticmethod
        @router.callback_query(F.data == 'choose author')
        async def choose_author(callback_query: CallbackQuery, session: AsyncSession):
            message = callback_query.message
            if message:
                current_author = await crud.get_current_defualt_author(message.chat.id, session)
                authors = await crud.get_all_authors_of_user(message.chat.id, session)
                await message.answer(f'Choose author. Current: {current_author.name}', reply_markup=kb.build_authors(authors=authors))
                
        @staticmethod
        @router.callback_query(F.data == 'back_to_settings')
        async def back_to_settings(callback_query: CallbackQuery):
            await callback_query.answer()
            await callback_query.message.edit_text('Select mode', reply_markup=kb.settings) # type:ignore
            
        class ChooseAuthor:
            ''' SET DEFAULT AUTHOR '''
            @staticmethod
            @router.callback_query(AuthorCallback.filter())
            async def choose_author(callback_query: CallbackQuery, callback_data: AuthorCallback, session: AsyncSession):
                
                message = callback_query.message
                if message:
                    result = await crud.set_default_author(message.chat.id, callback_data.author_id, session=session)
                    await message.answer(f'Success! {result}, {callback_data.author_id}')
                    
            ''' ADD NEW AUTHOR '''
            @staticmethod
            @router.callback_query(F.data == 'new_author')
            async def set_new_author_state(callback_query: CallbackQuery, state: FSMContext):
                await callback_query.answer()
                await callback_query.message.answer('Enter author name:') # type:ignore
                await state.set_state(AuthorState.new_author)
                """|"""
                """|"""
                """|"""
                """V"""
            @staticmethod
            @router.message(F.text, AuthorState.new_author)
            async def add_new_author(message: Message, session: AsyncSession, state: FSMContext):
                new_author = await crud.add_new_author(name=message.text, user_id=message.chat.id, session=session)
                if new_author:
                    authors = await crud.get_all_authors_of_user(message.chat.id, session)
                    await message.answer(f'author added: {new_author.name}', reply_markup=kb.build_authors(authors))
                else:
                    await message.answer('Already exist')
                    await state.clear()
                await state.clear()
                
            
            
        
        
        
    @staticmethod
    @router.callback_query(F.data == 'back_to_menu')
    async def back_to_menu(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Menu', reply_markup=kb.build_menu(callback_query.message.chat.id)) # type:ignore
        
        
    @staticmethod 
    @router.callback_query(F.data == 'frequency')
    async def choose_frequency(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Settings', reply_markup=kb.frequency_settings)
        

    class TimeSettings:
        @staticmethod 
        @router.callback_query((F.data == 'set_frequency') | (F.data == 'cancel_adding_frequency'))
        async def set_frequency(callback_query: CallbackQuery):
            await callback_query.answer()
            await callback_query.message.edit_text('Choose units of measurments ot set:', reply_markup=kb.frequency_units)
            
        class SetFrequency:
            @staticmethod 
            @router.callback_query(UnitsCallback.filter())
            async def choose_units(callback_query: CallbackQuery, callback_data: UnitsCallback, session: AsyncSession, state: FSMContext):
                await callback_query.answer()
                if callback_data.units == 'seconds':
                    await state.set_state(FrequencyState.seconds)
                elif callback_data.units == 'minutes':
                    await state.set_state(FrequencyState.minutes)
                elif callback_data.units == 'hours':
                    await state.set_state(FrequencyState.minutes)
                    
                await state.set_data({'multiplier': callback_data.multiplier})
                await callback_query.message.edit_text(f'Set interval in {callback_data.units}:', reply_markup=kb.cancel_adding_frequency)
                
            @staticmethod 
            
            @router.message(F.text, FrequencyState())
            async def set_interval(message: Message, session: AsyncSession, state: FSMContext):
                if any(char.isalpha() for char in message.text):
                    await message.answer('Try again. should contain only numbers', reply_markup=kb.cancel_adding_frequency)
                else:
                    multiplier = await state.get_value('multiplier')
                    seconds = int(message.text) * int(multiplier)
                    await crud.set_interval_in_seconds(
                        user_id=message.chat.id,
                        seconds=seconds,
                        session=session
                    )
                    await message.answer(f'interval is now {seconds} seconds')
                    await asyncio.sleep(12)
                    await message.answer(#type:ignore
                        "Menu", reply_markup=kb.build_menu(message.chat.id)#type:ignore
                    )  
                    await state.clear()
                
                
            
        
        
    
    
async def periodic_message(chat_id: int, session: AsyncSession):
    result = await crud.get_random_quote(chat_id, session)
    await bot.send_message(chat_id, f''' "{result}." \n \n © <b></b> ''', parse_mode='HTML', reply_markup=kb.turn_off) 
    

