from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database import crud
from bot.database.models.author import Author
from bot.layout.callbacks import AuthorCallback, UnitsCallback


menu_def = ['Get random quote','Turn on', 'Download quotes', 'Settings', 'Add quote']

chat_states = {}


def build_menu(chat_id, change=False):
    current_state = chat_states.get(chat_id, 'Turn on')
    
    if change:
        current_state = 'Turn off' if current_state == 'Turn on' else 'Turn on'
        chat_states[chat_id] = current_state
        
    keyboard_builder = InlineKeyboardBuilder()
    current_menu = menu_def.copy()
    
    current_menu[1] = current_state
    
    for item in current_menu:
        keyboard_builder.button(text=item, callback_data=item)
    
    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()
    

# SETTINGS
settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Mode', callback_data='choose_mode')],
    [InlineKeyboardButton(text='Frequency ', callback_data='frequency')],
    [InlineKeyboardButton(text='Back ↩️', callback_data='back_to_menu')],
])

choose_mode = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Mixed', callback_data='mixed_au')],
    [InlineKeyboardButton(text='Choose author', callback_data='choose author')],
    [InlineKeyboardButton(text='Back ↩️', callback_data='back_to_settings')],
])
    
frequency_settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Set interval frequency', callback_data='set_frequency')],
    [InlineKeyboardButton(text='Set time per day', callback_data='set_times')],
    [InlineKeyboardButton(text='Set certain time of the day', callback_data='set_time_day')],
])

frequency_units = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Set interval in seconds', callback_data=UnitsCallback(units='seconds', multiplier=1).pack())],
    [InlineKeyboardButton(text='Set interval in minutes', callback_data=UnitsCallback(units='minutes', multiplier=60).pack())],
    [InlineKeyboardButton(text='Set interval in hours', callback_data=UnitsCallback(units='hours', multiplier=3600).pack())],
])

cancel_adding_frequency = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Cancel', callback_data='cancel_adding_frequency')],
])


def build_authors(authors: list[Author]):
    keyboard_builder = InlineKeyboardBuilder()
    
    for author in authors:
        author_callback = AuthorCallback(author=author.name, author_id=author.id)
        keyboard_builder.button(text=author.name, callback_data=author_callback)

    keyboard_builder.button(text='New author', callback_data='new_author')
    
    keyboard_builder.button(text='Back to menu ↩️', callback_data='back_to_menu')
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()


#QUOTES
cancel_adding_new_quote = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Cancel', callback_data='cancel_quote')]
])

one_more_quote = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='One more', callback_data='one_more_quote')]
])

turn_off = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Turn off', callback_data='Turn off'),
     InlineKeyboardButton(text='Change frequency', callback_data='set_frequency')]
])
