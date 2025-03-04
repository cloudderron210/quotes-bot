from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from bot.layout import keyboards as kb


router = Router()

@router.callback_query(F.data == 'Settings')
async def settings(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text('Settings', reply_markup=kb.settings) # type:ignore

@staticmethod
@router.callback_query(F.data == 'choose_mode')
async def choose_mode(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text('Choose Mode:', reply_markup=kb.choose_mode) 
    
@router.callback_query(F.data == 'back_to_menu')
async def back_to_menu(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text('Menu', reply_markup=kb.build_menu(callback_query.message.chat.id)) 
