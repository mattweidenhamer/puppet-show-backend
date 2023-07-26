from django.urls import reverse
from rest_framework.test import (
    APIClient,
    APITestCase,
)
from unittest.mock import MagicMock, Mock, patch
import requests

from puppetshowapp.models.authentication_models import DiscordPointingUser

from puppetshowapp.secrets.test_raw import RAW_ME, FAKE_RAW_TOKEN


class MockDiscordTokenCallback:
    def raise_for_status(self):
        pass

    def json(self):
        return FAKE_RAW_TOKEN


class MockDiscordMeCallback:
    def raise_for_status(self):
        pass

    def json(self):
        return RAW_ME


class TokenExchangeTestCase(APITestCase):
    def setUp(self):
        self.mock_discord_token_callback = MagicMock()
        self.mock_discord_token_callback.raise_for_status = Mock(return_value=None)
        self.mock_discord_token_callback.json = Mock(return_value=FAKE_RAW_TOKEN)
        self.mock_discord_me_callback = MagicMock()
        self.mock_discord_me_callback.raise_for_status = Mock(return_value=None)
        self.mock_discord_me_callback.json = Mock(return_value=RAW_ME)
        self.mock_bad_callback = MagicMock()
        self.raise_for_status = Mock(side_effect=requests.HTTPError("Bad request"))

    # Test that when sending a user token to the endpoint, it authenticates via discord and returns a token.
    def test_token_exchange_existing(self):
        normal_user_1 = DiscordPointingUser.objects.create(
            discord_snowflake="249615304185872395"
        )

        with patch("requests.post", return_value=self.mock_discord_token_callback):
            with patch("requests.get", return_value=self.mock_discord_me_callback):
                url = reverse("token-exchange")
                client = APIClient()
                response = client.get(url, {"code": "test_token"})
        self.assertEqual(response.status_code, 302)
        updated_normal_user = DiscordPointingUser.objects.get(pk=normal_user_1.pk)
        self.assertEqual(
            updated_normal_user.discord_auth_token, FAKE_RAW_TOKEN["access_token"]
        )
        self.assertEqual(
            updated_normal_user.discord_refresh_token, FAKE_RAW_TOKEN["refresh_token"]
        )
        token = response.url.split("token=")[1]
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.get(reverse("user-info"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["discord_snowflake"], "249615304185872395")

    # Same as the above test, but the user doesn't exist in the database and should be created.
    def test_token_withuser(self):
        with patch("requests.post", return_value=self.mock_discord_token_callback):
            with patch("requests.get", return_value=self.mock_discord_me_callback):
                url = reverse("token-exchange")
                client = APIClient()
                response = client.get(url, {"code": "test_token"})
        self.assertEqual(response.status_code, 302)
        updated_normal_user = DiscordPointingUser.objects.get(
            discord_snowflake="249615304185872395"
        )
        self.assertEqual(
            updated_normal_user.discord_auth_token, FAKE_RAW_TOKEN["access_token"]
        )
        self.assertEqual(
            updated_normal_user.discord_refresh_token, FAKE_RAW_TOKEN["refresh_token"]
        )
        token = response.url.split("token=")[1]
        client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = client.get(reverse("user-info"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["discord_snowflake"], "249615304185872395")

    # Test that the endpoint returns a 400 error if the token is invalid or expired.
    def test_token_invalid(self):
        with patch("requests.post", return_value=self.mock_bad_callback):
            url = reverse("token-exchange")
            client = APIClient()
            response = client.get(url, {"code": "test_token"})
        self.assertEqual(response.status_code, 400)
