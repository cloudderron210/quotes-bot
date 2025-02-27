from aiogram.utils.keyboard import InlineKeyboardBuilder


menu_def = ['Get random quote','Turn on', 'Download quotes', 'Settings', 'Add quote']

chat_states = {}


def build_menu(chat_id, change=False):
    current_state = chat_states.get(chat_id, 'Turn on')
    
    keyboard_builder = InlineKeyboardBuilder()
    current_menu = menu_def.copy()
    
    current_menu[1] = current_state
    
    for item in current_menu:
        keyboard_builder.button(text=item, callback_data=item)
    
    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()
    
