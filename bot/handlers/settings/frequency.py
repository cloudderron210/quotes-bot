import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.layout.callbacks import AuthorCallback, SpamModeCallback, UnitsCallback
from bot.states import AuthorState, FrequencyState, Specifictime
from bot.layout import keyboards as kb


router = Router()

"""CHOOSE QUOTE SPAM MODE"""
@router.callback_query(F.data == 'choose_frequency')
async def choose_frequency(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text('Settings', reply_markup=kb.choose_spam_time_mode)

""" Set spam mode in db"""
@router.callback_query(SpamModeCallback.filter())
async def set_spam_mode(callback_query: CallbackQuery, callback_data: SpamModeCallback, session: AsyncSession):
    try:
        await crud.set_spam_mode(callback_query.message.chat.id, callback_data.name, session)
        await callback_query.message.answer('success!')
    except Exception as e:
        await callback_query.message.answer(f'{e}')

 
@router.callback_query(F.data == 'configure_frequency')
async def configure_frequency(callback_query: CallbackQuery, session: AsyncSession):
    await callback_query.answer()
    await callback_query.message.answer('Choose mode to configure:', reply_markup=kb.frequency_settings)
    

@router.callback_query((F.data == 'set_frequency') | (F.data == 'cancel_adding_frequency'))
async def set_frequency(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text('Choose units of measurments to set:', reply_markup=kb.frequency_units)
    
        
@router.callback_query(F.data == 'set_times')
async def set_time_perday(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer('How many times a day:')
    await state.set_state(FrequencyState.times_per_day)
    
    
@router.message(F.text, FrequencyState.times_per_day)
async def enter_times(message: Message, state: FSMContext, session):
    await crud.set_interval(user_id=message.chat.id, session=session, times_per_day=int(message.text))
    await state.clear()
    await message.answer(f'{message.text} times now')
        
         
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
@router.callback_query(F.data == 'set_time_day')
async def enter_time_placeholder(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer('Enter time you want to receive quote:', reply_markup=kb.set_times)
    await state.set_state(Specifictime.enter_time)
    await state.set_data({'times':[]})  
    
    
@router.message(F.text, Specifictime.enter_time)
async def enter_time(message: Message, state: FSMContext):
    current_times = await state.get_value('times')
    current_times.append(message.text)
    await state.set_data({'times': current_times})
    await message.answer(f'Enter time you want to receive quote: {await state.get_value('times')}', reply_markup=kb.set_times)
    
    
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
