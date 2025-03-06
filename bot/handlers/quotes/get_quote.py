from io import BytesIO
from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery, InputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.database.models import Author, Quote
from bot.database.models.users import FrequencyEnum
from bot.helpers import periodic_message, schedule_messages, start_periodic_messages 
from bot.layout import keyboards as kb
from bot.services.scheduler import scheduler 


router = Router()


@router.callback_query(
    (F.data == "Get random quote") | (F.data == "one_more_quote")
)
async def get_random_quote(callback_query: CallbackQuery, session: AsyncSession):
    quote_result = await crud.get_random_quote(
        callback_query.message.chat.id, session
    )
    if quote_result:
        await callback_query.answer()
        await callback_query.message.answer(
            f"""{quote_result[0]}. \n \n © <b>{quote_result[1]}</b> """, parse_mode='HTML', reply_markup=kb.one_more_quote
        )


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

@router.callback_query(F.data == "Download quotes")
async def download_quotes(callback_query: CallbackQuery, session: AsyncSession):
    quotes = await crud.get_quotes_of_default_author(callback_query.message.chat.id, session)
    quotes_str = '\n'.join(quotes)
    file = BytesIO(quotes_str.encode('utf-8'))
    buffered_file = BufferedInputFile(file.getvalue(), filename='quotes.txt')
    
    await callback_query.message.answer_document(document=buffered_file)
    # await callback_query.message.answer(f'{quotes_str}')
    

@router.callback_query(F.data == 'Turn off')
async def turn_off(callback_query: CallbackQuery):
    user_id = callback_query.message.chat.id
    await callback_query.message.edit_text("Turned off", reply_markup=kb.build_menu(user_id,change=True))  # type:ignore
    jobs = scheduler.get_jobs()
    for job in jobs:
        if job.id.startswith(f'{user_id}_'):
            scheduler.remove_job(job.id)
    await callback_query.message.answer(f'{len(jobs)} jobs deleted')
