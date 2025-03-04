import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.database.models import Author, Quote
from bot.database.models.users import FrequencyEnum
from bot.helpers import periodic_message, schedule_messages, start_periodic_messages 
from bot.layout.callbacks import AuthorCallback, SpamModeCallback, UnitsCallback
from bot.states import AuthorState, FrequencyState, Specifictime
from bot.layout import keyboards as kb
from bot.services.scheduler import scheduler 
from apscheduler.triggers.interval import IntervalTrigger


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
    async def add_quote(message: Message, session: AsyncSession):
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
        user_id = callback_query.message.chat.id
        current_mode = await crud.get_spam_mode(user_id, session)
        current_settings = await crud.get_frequency_settings(user_id, session)

        if current_mode == FrequencyEnum.INTERVAL:
            await start_periodic_messages(
                chat_id=user_id,
                seconds=current_settings.interval_seconds,
                session=session
            )
            await callback_query.message.answer( # type: ignore
                f"Okey, let`s go...{current_mode}",
                reply_markup=kb.build_menu(callback_query.message.chat.id, change=True), #type: ignore
            )  

        if current_mode == FrequencyEnum.TIMES_PER_DAY:
            await callback_query.message.answer( # type: ignore
                f"Okey, let`s go...{current_mode}",
                reply_markup=kb.build_menu(callback_query.message.chat.id, change=True), #type: ignore
            )  
            num_messages = current_settings.times_per_day
            await schedule_messages(
                chat_id=callback_query.message.chat.id,
                num_messages=num_messages,
                session=session
            )
        if current_mode == FrequencyEnum.SPECIFIC_TIMES:
            await schedule_messages(
                chat_id=callback_query.message.chat.id,
                times=current_settings.specific_times,
                session=session
            )
            
            await callback_query.message.answer( # type: ignore
                f"Okey, let`s go...{current_mode} {scheduler.get_jobs()}",
                reply_markup=kb.build_menu(callback_query.message.chat.id, change=True), #type: ignore
            )  
            
        
    @staticmethod
    @router.callback_query(F.data == 'Turn off')
    async def turn_off(callback_query: CallbackQuery):
        user_id = callback_query.message.chat.id
        await callback_query.message.edit_text("Turned off", reply_markup=kb.build_menu(user_id,change=True))  # type:ignore
        jobs = scheduler.get_jobs()
        for job in jobs:
            if job.id.startswith(f'{user_id}_'):
                scheduler.remove_job(job.id)
            
        await callback_query.message.answer(f'{len(jobs)}')
        # scheduler.remove_job(job_id=f'{callback_query.message.chat.id}')

        
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
    @router.callback_query(F.data == 'choose_frequency')
    async def choose_frequency(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Settings', reply_markup=kb.choose_spam_time_mode)

    @staticmethod 
    @router.callback_query(SpamModeCallback.filter())
    async def set_spam_mode(callback_query: CallbackQuery, callback_data: SpamModeCallback, session: AsyncSession):
        try:
            await crud.set_spam_mode(callback_query.message.chat.id, callback_data.name, session)
            await callback_query.message.answer('success!')
        except Exception as e:
            await callback_query.message.answer(f'{e}')
    
    @staticmethod 
    @router.callback_query(F.data == 'configure_frequency')
    async def configure_frequency(callback_query: CallbackQuery, session: AsyncSession):
        await callback_query.answer()
        await callback_query.message.answer('Choose mode to configure:', reply_markup=kb.frequency_settings)
        

    class TimeSettings:
        @staticmethod 
        @router.callback_query((F.data == 'set_frequency') | (F.data == 'cancel_adding_frequency'))
        async def set_frequency(callback_query: CallbackQuery):
            await callback_query.answer()
            await callback_query.message.edit_text('Choose units of measurments to set:', reply_markup=kb.frequency_units)
            
        class TimesPerDay:
            @staticmethod 
            @router.callback_query(F.data == 'set_times')
            async def set_time_perday(callback_query: CallbackQuery, state: FSMContext):
                await callback_query.answer()
                await callback_query.message.answer('How many times a day:')
                await state.set_state(FrequencyState.times_per_day)
                
            @staticmethod 
            @router.message(F.text, FrequencyState.times_per_day)
            async def enter_times(message: Message, state: FSMContext, session):
                await crud.set_interval(user_id=message.chat.id, session=session, times_per_day=int(message.text))
                await state.clear()
                await message.answer(f'{message.text} times now')
            
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
                    await crud.set_interval(
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



                    """ NEED TO BE IMPROVED"""
        class SetTimePerDay:
            @staticmethod 
            @router.callback_query(F.data == 'set_time_day')
            async def enter_time_placeholder(callback_query: CallbackQuery, state: FSMContext):
                await callback_query.answer()
                await callback_query.message.answer('Enter time you want to receive quote:', reply_markup=kb.set_times)
                await state.set_state(Specifictime.enter_time)
                await state.set_data({'times':[]})  
                
            @staticmethod 
            @router.message(F.text, Specifictime.enter_time)
            async def enter_time(message: Message, state: FSMContext):
                current_times = await state.get_value('times')
                current_times.append(message.text)
                await state.set_data({'times': current_times})
                await message.answer(f'Enter time you want to receive quote: {await state.get_value('times')}', reply_markup=kb.set_times)
                
            @staticmethod 
            @router.callback_query(F.data == 'set_specific_times')
            async def set_time(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
                current_times = await state.get_value('times')
                await crud.set_interval(
                    callback_query.message.chat.id,
                    session=session,
                    specific_times=current_times
                )
                await callback_query.message.answer(f'{current_times} has been set')
                await state.clear()
                

            
                

                
                
                















                
            
                    
                    
    

