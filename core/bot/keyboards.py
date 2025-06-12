from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu(language='uz'):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if language == 'uz':
        markup.add(KeyboardButton("Kategoriyalar"))
        markup.add(KeyboardButton("Savatcha"))
        markup.add(KeyboardButton("Buyurtmalar"))
        markup.add(KeyboardButton("Tilni o‘zgartirish"))
    else:
        markup.add(KeyboardButton("Категории"))
        markup.add(KeyboardButton("Корзина"))
        markup.add(KeyboardButton("Заказы"))
        markup.add(KeyboardButton("Изменить язык"))
    return markup

def get_categories_menu(categories, language='uz'):
    markup = InlineKeyboardMarkup()
    for category in categories:
        name = category.name_uz if language == 'uz' else category.name_ru
        markup.add(InlineKeyboardButton(name, callback_data=f"category_{category.id}"))
    return markup

def get_colors_menu(product, language='uz'):
    markup = InlineKeyboardMarkup()
    for color in product.colors.all():
        name = color.name_uz if language == 'uz' else color.name_ru
        markup.add(InlineKeyboardButton(f"{name} ({color.price} UGX)", callback_data=f"color_{color.id}"))
    return markup

def get_language_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("O‘zbek", callback_data="lang_uz"))
    markup.add(InlineKeyboardButton("Русский", callback_data="lang_ru"))
    return markup

def get_contact_button(language='uz'):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton("Telefon raqamni yuborish 📱", request_contact=True) if language == 'uz' else KeyboardButton("Отправить номер телефона 📱", request_contact=True)
    markup.add(button)
    return markup