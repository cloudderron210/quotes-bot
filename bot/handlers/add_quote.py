from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.database.models import Author, Quote
from bot.states import AuthorState
from bot.layout import keyboards as kb

router = Router()





@router.callback_query(F.data == 'Add quote')
async def add_quote_button(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    current_author: Author = await crud.get_current_defualt_author(callback_query.message.chat.id, session) # type:ignore
    await state.set_state(AuthorState.add_quote)
    await callback_query.message.edit_text(f'Enter new quote for {current_author.name}', reply_markup=kb.cancel_adding_new_quote) #type:ignore

    
@router.message(F.text, AuthorState.add_quote)
async def add_quote(message: Message, session: AsyncSession, state: FSMContext):
    current_author: Author = await crud.get_current_defualt_author(message.chat.id, session) # type:ignore
    new_quote = await crud.add_quote(author=current_author, text=message.text, session=session) # type:ignore
    
    await message.answer(f'{new_quote} has been added')
    await message.answer(f'Enter new quote for {current_author.name}', reply_markup = kb.cancel_adding_new_quote) # type:ignore
    
@router.callback_query(F.data == 'cancel_quote')
async def cancel_add_quote(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.edit_text('Menu', reply_markup=kb.build_menu(callback_query.message.chat.id)) # type:ignore
    await state.clear()
    
    
    

    
                    
    

# new_quote: Quote = await crud.add_quote(author=current_author, text='text', session=session)
