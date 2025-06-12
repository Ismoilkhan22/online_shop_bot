from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings
from core.bot.handlers import register_handlers

class Command(BaseCommand):
    help = 'Run Telegram bot'

    def handle(self, *args, **options):
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(bot=bot, storage=storage)

        # Handler'larni ro'yxatdan o'tkazish
        register_handlers(dp)

        self.stdout.write(self.style.SUCCESS('Bot started successfully'))
        import asyncio
        asyncio.run(dp.start_polling(allowed_updates=dp.resolve_used_update_types()))