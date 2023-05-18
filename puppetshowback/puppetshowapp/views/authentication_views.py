from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from ..models.authentication_models import DiscordPointingUser
from rest_framework import status
from rest_framework.authtoken.models import Token
import requests
import logging
from ..secrets.constants import (
    DISCORD_OAUTH_URL,
    DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET,
    API_ENDPOINT,
    DISCORD_AUTH_TOKEN_URL,
    DISCORD_USERS_REDIRECT,
    FRONTEND_REDIRECT,
)
import secrets


# This should be called to redirect the user to Discord's login page
# For testing purposes. In production this should be called from the frontend.
def login_redirect_discord(request):
    return redirect(DISCORD_OAUTH_URL)


def discord_user_callback(request):
    user = exchange_code_for_token(request)
    if isinstance(user, Exception):
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    if isinstance(user, DiscordPointingUser):
        # TODO implement django-rest-knox for better tokening.
        token, created = Token.objects.get_or_create(user=user)
        redirect_url = f"{FRONTEND_REDIRECT}?token={token.key}"
        return redirect(redirect_url)
    else:
        logging.error("Got abnormal user from request.")
        logging.error(user)
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def exchange_code_for_token(request):
    code = request.GET.get("code")
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_USERS_REDIRECT,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        token_exchange_response = requests.post(
            DISCORD_AUTH_TOKEN_URL, data=data, headers=headers, timeout=4
        )
        token_exchange_response.raise_for_status()
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            return e
    token_data = token_exchange_response.json()
    access_token = token_data["access_token"]
    try:
        response = requests.get(
            f"{API_ENDPOINT}/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=4,
        )
        response.raise_for_status()
        user_data = response.json()
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        return e
    discord_id = user_data["id"]
    user, created = DiscordPointingUser.objects.get_or_create(
        discord_snowflake=discord_id
    )
    user.discord_auth_token = access_token
    user.discord_refresh_token = token_data["refresh_token"]
    user.discord_avatar = user_data["avatar"]
    if created:
        user.discord_username = user_data["username"]
        user.login_username = user_data["username"]
    user.save()

    return user


def discord_user_logout(request):
    logout(request)
    return redirect("/")
