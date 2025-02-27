from aiogram.types import InlineKeyboardButton as InKB, InlineKeyboardMarkup, KeyboardButton as KB, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.mysql_connection import get_authors_list

# INLINE KEYBOARDS 
authors = ['Jason Statham 🧔', 'Don Juan 🗿']
menu_def = ['Get random quote','Turn on', 'Download quotes', 'Settings', 'Add quote']
settings = ['Change Author', 'Change frequency']
chat_states = {}
authors_per_user = {}

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

def build_authors_list(user_id):
    result_raw = get_authors_list(user_id)
    authors = [author[0] for author in result_raw]
    return(authors)


def build_frequency():
    keyboard_builder = InlineKeyboardBuilder()
    variants = ['-30 min', '-10 min', '-1 min', '-5 sec', '-1 sec ','+1 sec','+5 sec', '+1 min', '+10 min', '+30 min']
    
    
    for var in variants:
        keyboard_builder.button(text=var, callback_data=var)

    keyboard_builder.button(text='Back to menu ↩️', callback_data='back_to_menu')
    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()
    
    
def build_authors(chat_id, new_author=None):
        
    user_authors = build_authors_list(user_id=chat_id)
    keyboard_builder = InlineKeyboardBuilder()
        
    for author in user_authors:
        keyboard_builder.button(text=author, callback_data=f'{author}_au')

    keyboard_builder.button(text='New author', callback_data='new_author')
    
    keyboard_builder.button(text='Back to menu ↩️', callback_data='back_to_menu')
        
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
    
    
    
    
    
frequency_settings = InlineKeyboardMarkup(inline_keyboard=[
    [InKB(text='Set interval frequency', callback_data='set_frequency')],
    [InKB(text='Set time per day', callback_data='set_times')],
    [InKB(text='Set certain time of the day', callback_data='set_time_day')],
])

choose_author = InlineKeyboardMarkup(inline_keyboard=[
    [InKB(text='Jason Statham 🧔', callback_data='jason_statham')],
    [InKB(text='Don Juan 🗿', callback_data='don_juan')],
])

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InKB(text='Mode', callback_data='choose_mode')],
    [InKB(text='Frequency ', callback_data='frequency')],
    [InKB(text='Back ↩️', callback_data='back_to_menu')],
])



choose_mode = InlineKeyboardMarkup(inline_keyboard=[
    [InKB(text='Mixed', callback_data='mixed_au')],
    [InKB(text='Choose author', callback_data='Choose author')],
    [InKB(text='Back ↩️', callback_data='back_to_settings')],
])

cancel_adding_new_quote = InlineKeyboardMarkup(inline_keyboard=[
    [InKB(text='Cancel', callback_data='cancel_quote')]
])

one_more_quote = InlineKeyboardMarkup(inline_keyboard=[
    [InKB(text='One more', callback_data='one_more_quote')]
])

turn_off = InlineKeyboardMarkup(inline_keyboard=[
    [InKB(text='Turn off', callback_data='Turn off'),InKB(text='Change frequency', callback_data='set_frequency')]
])





# REPLY KEYBOARDS

reply_keyboard_on = ReplyKeyboardMarkup(keyboard=[
    [KB(text='* Turn on *'),],
    [KB(text='* - 1 s *'), KB(text='* + 1 s *')],
], resize_keyboard=True, input_field_placeholder='Choose something below')

reply_keyboard_off = ReplyKeyboardMarkup(keyboard=[
    [KB(text='* Turn off *'),],
    [KB(text='* - 1 s *'), KB(text='* + 1 s *')],
], resize_keyboard=True, input_field_placeholder='Choose something below')



