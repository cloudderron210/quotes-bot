import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, InputFile, Message 
from bot_instance import bot
from scheduler import scheduler
from bot.mysql_connection import add_misc_quote, get_all_authors, get_authors_list, get_default_author, get_interval_seconds, get_random_message, insert_new_author, set_default_author, set_interval_seconds, set_user_authors, check_default_author
from bot.sql.sqlorm import add_quote_2, add_misc_quote_2, get_default_author_2, get_random_message_2, set_default_author_2
from apscheduler.triggers.interval import IntervalTrigger # type:ignore
from bot.layout import keyboard as kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


callback_router = Router()

class AuthorState(StatesGroup):
    new_author = State()
    add_quote = State()
    add_misc_quote = State()
    add_quote_author = State()
    set_interval_seconds = State()

    
@callback_router.message(Command('check'))
async def check(message: Message):
    user_id = message.chat.id
    try:
        result = check_default_author(user_id)
        await message.answer(f'{result}')
    except Exception as e:
        await message.answer(f'{e}')
        
        


def save_quotes_to_file(quotes, file_path, user_id, mixed=False):
    current_author = get_default_author(user_id)
    if mixed == False: 
        with open(file_path, 'w') as file:
            for quote in quotes:
                file.write(f'{quote[0]} - {current_author} \n \n ')
    elif mixed == True:
        with open(file_path, 'w') as file:
            for quote in quotes:
                file.write(f'{quote[0]} - {quote[1]} \n \n ')
        
        
class Menu:
    @staticmethod
    @callback_router.callback_query((F.data == 'Download quotes')) 
    async def send_txt(callback_query: CallbackQuery):
        path = 'quotes.txt'
        current_author = get_default_author(callback_query.message.chat.id)
        await callback_query.message.answer(f'{current_author}')
        if current_author == 'mixed':
            await callback_query.message.answer('chebur')
            quotes = get_random_message(callback_query.message.chat.id, mixed=True, limit=1000) # type:ignore
            save_quotes_to_file(quotes, path, callback_query.message.chat.id, mixed=True) # type:ignore
        else:
            quotes = get_random_message(callback_query.message.chat.id, limit=1000) # type:ignore
            save_quotes_to_file(quotes, path, callback_query.message.chat.id) # type:ignore
                                        
        document = FSInputFile(path, filename=f'{current_author}.txt')
        await callback_query.message.answer_document(document) # type:ignore
        os.remove(path)
    
    
    @staticmethod
    @callback_router.callback_query((F.data == 'Get random quote') | (F.data == 'one_more_quote'))
    async def get_random(callback_query: CallbackQuery):
        try:
            current = get_default_author(callback_query.message.chat.id) # type:ignore
            if current == 'mixed':
                result = get_random_message_2(str(callback_query.message.chat.id), mixed=True) # type:ignore
                await callback_query.answer()
                await callback_query.message.answer(f''' "{result[0]}." \n \n © <b>{result[1]}</b> ''', parse_mode='HTML', reply_markup=kb.one_more_quote) # type:ignore
            else:
                random_message = get_random_message_2(callback_query.message.chat.id) # type:ignore
                await callback_query.answer()
                await callback_query.message.answer(f'''LEL {random_message}. \n \n © <b>{current}</b> ''', parse_mode='HTML', reply_markup=kb.one_more_quote) # type:ignore
        except Exception as e:
            await callback_query.message.answer(f'{e}') # type:ignore
    

    @staticmethod
    @callback_router.callback_query(F.data == 'Turn on')
    async def turn_on(callback_query: CallbackQuery):
        await callback_query.message.answer("Okey, let`s go...", reply_markup=kb.build_menu(callback_query.message.chat.id, change=True))  # type:ignore
        current_interval = get_interval_seconds(callback_query.message.chat.id) # type:ignore
        scheduler.add_job(periodic_message, IntervalTrigger(seconds=current_interval), args=[callback_query.message.chat.id], id='random_message')  # type:ignore

    @staticmethod
    @callback_router.callback_query(F.data == 'Turn off')
    async def turn_off(callback_query: CallbackQuery):
        await callback_query.message.edit_text("Turned off", reply_markup=kb.build_menu(callback_query.message.chat.id,change=True))  # type:ignore
        await callback_query.message.answer(f'{kb.chat_states}') # type:ignore
        scheduler.remove_job(job_id='random_message')

    @staticmethod
    @callback_router.callback_query(F.data == 'Settings')
    async def settings(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Settings', reply_markup=kb.settings) # type:ignore

    @staticmethod
    @callback_router.callback_query(F.data == 'Add quote')
    async def add_quote_button(callback_query: CallbackQuery, state: FSMContext):
        current_author  = get_default_author_2(callback_query.message.chat.id) # type:ignore
        print(f'{current_author}')
        if current_author == 'mixed':
            await state.set_state(AuthorState.add_misc_quote)
            await callback_query.message.answer('Enter misc quote: ', reply_markup=kb.cancel_adding_new_quote) # type:ignore
        else:
            await state.set_state(AuthorState.add_quote)
            await callback_query.message.edit_text(f'Enter new quote for {current_author}', reply_markup = kb.cancel_adding_new_quote) # type:ignore
            
    @staticmethod
    @callback_router.message(F.text, AuthorState.add_misc_quote)
    async def add_misc_quote(message: Message, state: FSMContext):
        await state.update_data(quote_text=message.text)
        await state.set_state(AuthorState.add_quote_author)
        await message.answer('Who said that?', reply_markup=kb.cancel_adding_new_quote)
        
    @staticmethod
    @callback_router.message(F.text, AuthorState.add_quote_author)
    async def add_misc_quote_author(message: Message, state: FSMContext):
        await state.update_data(quote_author=message.text)
        data = await state.get_data()
        try:
            result = add_misc_quote_2(data['quote_author'], data['quote_text'], message.chat.id)
            await message.answer(f'{result} lols')
            await state.clear()
        except Exception as e:
            print(f'{e}')
        
    @staticmethod
    @callback_router.message(F.text, AuthorState.add_quote)
    async def add_quote(message: Message, state: FSMContext):
        try:
            result = add_quote_2(message.chat.id, message.text)
            await message.answer(f'The quote has been added: {result}')
            current_author  = get_default_author(message.chat.id) # type:ignore
            await message.answer(f'Enter new quote for {current_author}', reply_markup = kb.cancel_adding_new_quote) # type:ignore
        except Exception as e:
            await message.answer(f'{e}')

    @staticmethod
    @callback_router.callback_query(F.data == 'cancel_quote')
    async def cancel_add_quote(callback_query: CallbackQuery, state: FSMContext):
        await callback_query.answer()
        await callback_query.message.edit_text('Menu', reply_markup=kb.build_menu(callback_query.message.chat.id)) # type:ignore
        await state.clear()
        
class Settings:
    @staticmethod
    @callback_router.callback_query(F.data == 'choose_mode')
    async def choose_mode(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Choose mode', reply_markup=kb.choose_mode)
    
    @staticmethod
    @callback_router.callback_query(F.data == 'frequency')
    async def frequency(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Settings', reply_markup=kb.frequency_settings)

    @staticmethod
    @callback_router.callback_query(F.data == 'back_to_menu')
    async def back_to_menu(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Menu', reply_markup=kb.build_menu(callback_query.message.chat.id)) # type:ignore
    
class ChooseMode:              
    # @staticmethod
    # @callback_router.callback_query(F.data == 'Mixed')
    # async def choose_mixed(callback_query: CallbackQuery):
    #     try:
    #         set_default_author(callback_query.message.chat.id, 'mixed')
    #     except Exception as e:
    #         print(f'e')
            
        
    @staticmethod 
    @callback_router.callback_query(F.data == 'Choose author')
    async def choose_author(callback_query: CallbackQuery):
        current = get_default_author(callback_query.message.chat.id) # type:ignore
        await callback_query.answer()
        await callback_query.message.edit_text(f'Choose author. Current: {current}', reply_markup=kb.build_authors(callback_query.message.chat.id)) # type:ignore
        
    @staticmethod
    @callback_router.callback_query(F.data == 'back_to_settings')
    async def back_to_settings(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Select mode', reply_markup=kb.settings) # type:ignore
        
        
class ChooseAuthor: 
    @staticmethod
    @callback_router.callback_query(F.data.regexp(r'.*_au$'))
    async def set_def_author(callback_query: CallbackQuery): 
        try:
            res = set_default_author_2(callback_query.message.chat.id, str(callback_query.data[:-3])) # type:ignore
            current = get_default_author(callback_query.message.chat.id) # type:ignore
            await callback_query.message.edit_text(f'Choose author. Current: {current}', reply_markup=kb.build_authors(callback_query.message.chat.id)) # type:ignore
            await callback_query.message.answer(f'{current} has been set as default')
            callback_query.answer(f'{current} has been set')
            print('successfully defaulted')
        except Exception as e:
            await callback_query.message.answer(f'{e}') # type:ignore
            print(f'{e}, {callback_query.data[:-3]}')
    
    @staticmethod
    @callback_router.callback_query(F.data == 'new_author')
    async def new_author_add(callback_query: CallbackQuery, state: FSMContext):
        await callback_query.answer()
        await callback_query.message.answer('Enter author name') # type:ignore
        await state.set_state(AuthorState.new_author)

    @staticmethod
    @callback_router.message(F.text, AuthorState.new_author)
    async def new_author(message: Message, state: FSMContext):
        try:
            set_user_authors(message.chat.id, new_author=message.text)
            print('success!')
        except Exception as e:
            print(f'{e}')
            await message.answer('author already exists')
        await message.answer(f'{message.text} added to authors', reply_markup=kb.build_authors(message.chat.id))
        await state.clear()
        
    @staticmethod
    @callback_router.message(Command('get'))
    async def get_authors(message: Message):
        try:
            result = get_all_authors()
            authors = [author[0] for author in result]
            await message.answer(f'{authors}')
        except Exception as e:
            print(f'error: {e}')

    
    @staticmethod
    @callback_router.callback_query(F.data == 'back_to_mode_select')
    async def back_to_mode(callback_query: CallbackQuery):
        await callback_query.answer()
        await callback_query.message.edit_text('Select mode', reply_markup=kb.choose_mode) # type:ignore
        
class SetFrequency:
    @staticmethod
    @callback_router.callback_query(F.data == 'set_frequency')
    async def set_seconds_interval_state(callback_query: CallbackQuery, state: FSMContext):
        current_interval = get_interval_seconds(callback_query.message.chat.id)
        await callback_query.answer()
        await callback_query.message.answer(f'Set time in seconds. Current: {current_interval}', reply_markup=kb.build_frequency()) # type:ignore
        
        ''' FOR BUTTON ENTER SECONDS '''
    @staticmethod
    @callback_router.callback_query((F.data.regexp(r'.*min|.*sec')) )
    async def set_def_author(callback_query: CallbackQuery): 
        await callback_query.answer()
        current_interval = get_interval_seconds(callback_query.message.chat.id)
        if 'sec' in callback_query.data: # type:ignore
            desired_interval = current_interval + int(callback_query.data[:3]) # type:ignore
        if 'min' in callback_query.data: # type:ignore
            desired_interval = current_interval + int(callback_query.data[:3]) * 60 # type:ignore
        
        if desired_interval > 0:  # type:ignore
            try:
                set_interval_seconds(callback_query.message.chat.id, desired_interval) # type:ignore
                current_interval = get_interval_seconds(callback_query.message.chat.id) # type:ignore
                await callback_query.message.answer(f'interval has been set. {current_interval}') # type:ignore
                scheduler.modify_job(job_id='random_message', trigger=IntervalTrigger(seconds=current_interval))
                
            except Exception as e:
                print(f'{e}')
        else:
            await callback_query.message.answer('interval cant be lower than 0')
        
            
async def periodic_message(chat_id: int):
    current = get_default_author(chat_id)
    if current == 'mixed':
        result = get_random_message(chat_id, mixed=True)
        await bot.send_message(chat_id ,f''' {result[0]} \n \n © <b>{result[1]}</b> ''', parse_mode='HTML', reply_markup=kb.turn_off) # type:ignore
    else:
        result = get_random_message(chat_id)
        await bot.send_message(chat_id, f''' "{result[0][0]}." \n \n © <b>{current}</b> ''', parse_mode='HTML', reply_markup=kb.turn_off) # type:ignore
    




    
