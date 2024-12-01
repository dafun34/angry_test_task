import os
import django
from django.core.management.base import BaseCommand
from telegram.ext import ApplicationBuilder, CommandHandler
from bot.command_handler import start
from config import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "telegram_auth.settings")


class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def handle(self, *args, **options):
        django.setup()

        application = ApplicationBuilder().token(config.bot_token).build()
        start_handler = CommandHandler("start", start)
        application.add_handler(start_handler)

        self.stdout.write("Бот запущен")
        application.run_polling()
