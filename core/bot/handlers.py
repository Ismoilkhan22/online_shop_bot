from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.contrib.auth.models import User
from core.models import Category, Product, Cart, CartItem, Color, Order, UserProfile
from core.bot.keyboards import get_main_menu, get_categories_menu, get_colors_menu, get_language_menu, \
    get_contact_button
from core.bot.states import RegistrationStates, CartStates, LanguageStates


def register_handlers(dp: Dispatcher):
    @dp.message(commands=['start'])
    async def start_command(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        username = message.from_user.username or f"user_{user_id}"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'first_name': message.from_user.first_name or ''}
        )

        if created or not hasattr(user, 'profile'):
            UserProfile.objects.get_or_create(user=user)
            await message.answer("Xush kelibsiz! Tilni tanlang:", reply_markup=get_language_menu())
            await LanguageStates.select_language.set()
        else:
            language = user.profile.language
            await message.answer("Xush kelibsiz!" if language == 'uz' else "Добро пожаловать!",
                                 reply_markup=get_main_menu(language))
            await state.finish()

    @dp.callback_query(lambda c: c.data.startswith('lang_'), state=LanguageStates.select_language)
    async def process_language(callback_query: types.CallbackQuery, state: FSMContext):
        language = callback_query.data.split('_')[1]
        user = User.objects.get(username=callback_query.from_user.username or f"user_{callback_query.from_user.id}")
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.language = language
        profile.save()

        await callback_query.message.answer("Ismingizni kiriting:" if language == 'uz' else "Введите ваше имя:",
                                            reply_markup=types.ReplyKeyboardRemove())
        await RegistrationStates.first_name.set()
        await callback_query.answer()

    @dp.message(state=RegistrationStates.first_name)
    async def process_first_name(message: types.Message, state: FSMContext):
        await state.update_data(first_name=message.text)
        language = (await state.get_data()).get('language', 'uz')
        await message.answer("Familiyangizni kiriting:" if language == 'uz' else "Введите фамилию:")
        await RegistrationStates.last_name.set()

    @dp.message(state=RegistrationStates.last_name)
    async def process_last_name(message: types.Message, state: FSMContext):
        data = await state.get_data()
        first_name = data['first_name']
        language = data.get('language', 'uz')

        user = User.objects.get(username=message.from_user.username or f"user_{message.from_user.id}")
        user.first_name = first_name
        user.last_name = message.text
        user.save()

        await message.answer("Telefon raqamingizni yuboring:" if language == 'uz' else "Отправьте номер телефона:",
                             reply_markup=get_contact_button(language))
        await RegistrationStates.phone_number.set()

    @dp.message(content_types=types.ContentType.CONTACT, state=RegistrationStates.phone_number)
    async def process_phone_number(message: types.Message, state: FSMContext):
        phone_number = message.contact.phone_number
        user = User.objects.get(username=message.from_user.username or f"user_{message.from_user.id}")
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone_number = phone_number
        profile.save()

        language = profile.language
        await message.answer("Ro'yxatdan o'tdingiz!" if language == 'uz' else "Вы зарегистрированы!",
                             reply_markup=get_main_menu(language))
        await state.finish()

    @dp.message(lambda message: message.text in ["Kategoriyalar", "Категории"])
    async def show_categories(message: types.Message):
        user = User.objects.get(username=message.from_user.username or f"user_{message.from_user.id}")
        language = user.profile.language
        categories = Category.objects.filter(parent__isnull=True)
        if categories.exists():
            await message.answer("Kategoriyalarni tanlang:" if language == 'uz' else "Выберите категорию:",
                                 reply_markup=get_categories_menu(categories, language))
        else:
            await message.answer("Hozircha kategoriyalar mavjud emas." if language == 'uz' else "Пока нет категорий.")

    @dp.callback_query(lambda c: c.data.startswith('category_'))
    async def process_category(callback_query: types.CallbackQuery):
        category_id = int(callback_query.data.split('_')[1])
        category = Category.objects.get(id=category_id)
        user = User.objects.get(username=callback_query.from_user.username or f"user_{callback_query.from_user.id}")
        language = user.profile.language

        subcategories = category.children.all()
        products = category.products.all()

        if subcategories:
            await callback_query.message.answer(
                f"{category.name_uz if language == 'uz' else category.name_ru} subkategoriyalari:",
                reply_markup=get_categories_menu(subcategories, language))
        elif products:
            for product in products:
                name = product.name_uz if language == 'uz' else product.name_ru
                desc = product.description_uz if language == 'uz' else product.description_ru
                await callback_query.message.answer(f"{name}\n{desc}\nNarx: Tanlash uchun rangni bosing",
                                                    reply_markup=get_colors_menu(product, language))
        else:
            await callback_query.answer(
                "Bu kategoriyada hech narsa yo‘q." if language == 'uz' else "В этой категории ничего нет.")

        await callback_query.answer()

    @dp.callback_query(lambda c: c.data.startswith('color_'), state='*')
    async def process_color(callback_query: types.CallbackQuery, state: FSMContext):
        color_id = int(callback_query.data.split('_')[1])
        user = User.objects.get(username=callback_query.from_user.username or f"user_{callback_query.from_user.id}")
        language = user.profile.language

        await state.update_data(color_id=color_id)
        await callback_query.message.answer(
            "Mahsulotni savatchaga qo‘shish uchun ID ni kiriting:" if language == 'uz' else "Введите ID товара для добавления в корзину:")
        await CartStates.select_product.set()
        await callback_query.answer()

    @dp.message(state=CartStates.select_product)
    async def process_add_to_cart(message: types.Message, state: FSMContext):
        try:
            product_id = int(message.text)
            data = await state.get_data()
            color_id = data['color_id']
            product = Product.objects.get(id=product_id)
            color = Color.objects.get(id=color_id)
            user = User.objects.get(username=message.from_user.username or f"user_{message.from_user.id}")
            language = user.profile.language

            cart = Cart.objects.filter(user=user).latest('created_at') or Cart.objects.create(user=user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, color=color)
            if not created:
                cart_item.quantity += 1
                cart_item.save()

            await message.answer(
                f"{product.name_uz if language == 'uz' else product.name_ru} ({color.name_uz if language == 'uz' else color.name_ru}) savatchaga qo‘shildi!")
            await state.finish()
        except Product.DoesNotExist:
            await message.answer("Bunday mahsulot topilmadi." if language == 'uz' else "Товар не найден.")
        except Exception as e:
            await message.answer(f"Xato: {str(e)}")
            await state.finish()

    @dp.message(lambda message: message.text in ["Savatcha", "Корзина"])
    async def show_cart(message: types.Message):
        user = User.objects.get(username=message.from_user.username or f"user_{message.from_user.id}")
        language = user.profile.language
        try:
            cart = Cart.objects.filter(user=user).latest('created_at')
            items = cart.items.all()

            if items:
                response = "\n".join([
                                         f"{item.quantity} x {item.product.name_uz if language == 'uz' else item.product.name_ru} ({item.color.name_uz if language == 'uz' else item.color.name_ru}) - {item.color.price * item.quantity} UGX"
                                         for item in items])
                markup = InlineKeyboardMarkup()
                for item in items:
                    markup.add(InlineKeyboardButton(
                        f"O‘chirish: {item.product.name_uz if language == 'uz' else item.product.name_ru}",
                        callback_data=f"delete_{item.id}"))
                markup.add(InlineKeyboardButton("Buyurtma berish" if language == 'uz' else "Оформить заказ",
                                                callback_data="start_order"))
                await message.answer(f"Savatchangiz:\n{response}" if language == 'uz' else f"Ваша корзина:\n{response}",
                                     reply_markup=markup)
            else:
                await message.answer("Savatchangiz bo‘sh." if language == 'uz' else "Ваша корзина пуста.")
        except Cart.DoesNotExist:
            await message.answer("Savatchangiz bo‘sh." if language == 'uz' else "Ваша корзина пуста.")

    @dp.callback_query(lambda c: c.data.startswith('delete_'))
    async def delete_cart_item(callback_query: types.CallbackQuery):
        item_id = int(callback_query.data.split('_')[1])
        user = User.objects.get(username=callback_query.from_user.username or f"user_{callback_query.from_user.id}")
        language = user.profile.language

        try:
            item = CartItem.objects.get(id=item_id)
            item.delete()
            await callback_query.message.answer(
                "Mahsulot savatchadan o‘chirildi!" if language == 'uz' else "Товар удалён из корзины!")
        except CartItem.DoesNotExist:
            await callback_query.answer("Xato: Mahsulot topilmadi." if language == 'uz' else "Ошибка: товар не найден.")
        await callback_query.answer()

    @dp.callback_query(lambda c: c.data == 'start_order')
    async def start_order(callback_query: types.CallbackQuery):
        user = User.objects.get(username=callback_query.from_user.username or f"user_{callback_query.from_user.id}")
        language = user.profile.language
        try:
            cart = Cart.objects.filter(user=user).latest('created_at')
            items = cart.items.all()
            if items:
                total = sum(item.color.price * item.quantity for item in items)
                order = Order.objects.create(user=user, total_price=total)
                await callback_query.message.answer(
                    "Buyurtma boshlandi! Tez orada siz bilan bog‘lanamiz." if language == 'uz' else "Заказ начат! Скоро с вами свяжемся.")
                cart.delete()
            else:
                await callback_query.message.answer(
                    "Savatchangiz bo‘sh." if language == 'uz' else "Ваша корзина пуста.")
        except Cart.DoesNotExist:
            await callback_query.message.answer("Savatchangiz bo‘sh." if language == 'uz' else "Ваша корзина пуста.")
        await callback_query.answer()

    @dp.message(lambda message: message.text in ["Tilni o‘zgartirish", "Изменить язык"])
    async def change_language(message: types.Message):
        await message.answer("Tilni tanlang:" if message.text == "Tilni o‘zgartirish" else "Выберите язык:",
                             reply_markup=get_language_menu())
        await LanguageStates.select_language.set()