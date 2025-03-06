from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.layout import keyboards as kb
from bot.states import AuthorState
from bot.layout.callbacks import AuthorCallback
from bot.database import crud

router = Router()

''' MIXED '''
@router.callback_query(F.data == 'mixed_au')
async def mixed(callback_query: CallbackQuery):
    pass
    
'''CHOOSE AUTHOR'''
@router.callback_query(F.data == 'choose author')
async def choose_author(callback_query: CallbackQuery, session: AsyncSession):
    message = callback_query.message
    if message:
        current_author = await crud.get_current_defualt_author(message.chat.id, session)
        authors = await crud.get_all_authors_of_user(message.chat.id, session)
        await message.answer(f'Choose author. Current: {current_author.name}', reply_markup=kb.build_authors(authors=authors))
        

''' SET DEFAULT AUTHOR '''
@router.callback_query(AuthorCallback.filter())
async def set_default_author(callback_query: CallbackQuery, callback_data: AuthorCallback, session: AsyncSession):
    message = callback_query.message
    if message:
        result = await crud.set_default_author(message.chat.id, callback_data.author_id, session=session)
        await message.answer(f'{callback_data.author_id} is now default')
        
''' ADD NEW AUTHOR '''
@router.callback_query(F.data == 'new_author')
async def set_new_author_state(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer('Enter author name:') # type:ignore
    await state.set_state(AuthorState.new_author)
    
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
        
    
@router.callback_query(F.data == 'back_to_settings')
async def back_to_settings(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text('Select mode', reply_markup=kb.settings) # type:ignore

