from aiogram.types import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database import crud


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


def build_authors(authors: list, new_author=None):
    keyboard_builder = InlineKeyboardBuilder()
    for author in authors:
        keyboard_builder.button(text=author, callback_data=f'{author}_au')

    keyboard_builder.button(text='New author', callback_data='new_author')
    
    keyboard_builder.button(text='Back to menu ↩️', callback_data='back_to_menu')
        
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()

# def build_authors(chat_id, new_author=None):
#         
#     # user_authors = crud.(user_id=chat_id)
#     keyboard_builder = InlineKeyboardBuilder()
#         
#     for author in user_authors:
#         keyboard_builder.button(text=author, callback_data=f'{author}_au')
#
#     keyboard_builder.button(text='New author', callback_data='new_author')
#     
#     keyboard_builder.button(text='Back to menu ↩️', callback_data='back_to_menu')
#         
#     keyboard_builder.adjust(1)
#     return keyboard_builder.as_markup()

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
