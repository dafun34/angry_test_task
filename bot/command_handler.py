import requests
from telegram import Update
from telegram.ext import ContextTypes

from auth_app.models import User, AuthToken
from config import config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start.
    Получает токен из команды и связывает Telegram-аккаунт с пользователем.
    """
    args = context.args
    if not args:
        await update.message.reply_text("Ошибка: отсутствует токен.")
        return

    token = args[0]

    try:
        auth_token = await AuthToken.objects.aget(token=token)
        if not auth_token.is_valid():
            await update.message.reply_text("Ошибка: токен недействителен или устарел.")
            return

        telegram_user = update.effective_user
        user, is_created = await User.objects.aget_or_create(
            telegram_id=telegram_user.id, telegram_username=telegram_user.username)
        auth_token.user = user
        await auth_token.asave()
        response = requests.post(
            f"http://{config.django_host}:{config.django_port}/telegram-callback/",
            json={"token": token}
        )
        if response.status_code == 200:
            await update.message.reply_text("Вы успешно авторизованы!")
        else:
            await update.message.reply_text("Ошибка авторизации!")

    except Exception as exc:
        await update.message.reply_text(f"Ошибка: {repr(exc)}")
