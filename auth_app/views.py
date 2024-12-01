import json
from datetime import timedelta

from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from config import config
from .models import AuthToken


def home(request):
    """
    Отображает домашнюю страницу с формой для авторизации через Telegram.

    :param request: HTTP запрос
    :return: HTML страница с формой для авторизации через Telegram
    """
    if request.session.session_key:
        user = AuthToken.objects.get(token=request.session.session_key).user
        if user.is_authenticated:
            return render(
                request, 'home.html', {
                    "user": {
                        "telegram_username": user.telegram_username,
                        "telegram_id": user.telegram_id
                    }
                }
            )
    return render(request, 'login.html')


def telegram_login(request):
    """
    Генерирует уникальный токен для авторизации через Telegram и создает запись
    в базе данных для данного токена. Возвращает URL для авторизации через Telegram.

    :param request: HTTP запрос
    :return: JsonResponse с URL для перехода в Telegram с уникальным токеном
    """
    request.session.save()
    unique_token = request.session.session_key
    expiration_time = now() + timedelta(minutes=10)

    AuthToken.objects.create(
        user=request.user if request.user.is_authenticated else None,
        token=unique_token,
        expiration_time=expiration_time,
    )
    redirect_url = f'https://t.me/{config.bot_name}?start={unique_token}'
    return JsonResponse({'redirect_url': redirect_url})


@csrf_exempt
def telegram_callback(request):
    """
    Обрабатывает callback запрос от Telegram после успешной авторизации пользователя.
    Проверяет токен, если он валиден, выполняет авторизацию пользователя в Django.

    :param request: HTTP запрос, содержащий токен от Telegram
    :return: JsonResponse с результатом операции
    """
    body = json.loads(request.body)
    token = body.get("token")
    if not token:
        return JsonResponse({"error": "Token not provided."}, status=400)

    try:
        auth_token = AuthToken.objects.get(token=token, used=False)
        if auth_token.is_valid():
            login(request, auth_token.user)
            auth_token.used = True
            auth_token.save()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"error": "Invalid or expired token."}, status=400)
    except AuthToken.DoesNotExist:
        return JsonResponse({"error": "Token not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)


def auth_status(request):
    """
    Проверяет статус авторизации пользователя на основе сессионного ключа.
    Возвращает информацию о пользователе, если он авторизован.

    :param request: HTTP запрос
    :return: JsonResponse с информацией о пользователе и статусом авторизации
    """
    response_template = {"is_authenticated": False, "user": None}
    session_key = request.session.session_key
    try:
        auth = AuthToken.objects.get(token=session_key)
        user = auth.user
        if user:
            response_template["is_authenticated"] = user.is_authenticated
            response_template["user"] = {
                "telegram_username": user.telegram_username,
                "telegram_id": user.telegram_id
            }
        return JsonResponse(response_template)
    except AuthToken.DoesNotExist:
        return JsonResponse({"is_authenticated": False, "user": None})
