from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import DiscordPointingUser


class CustomUserCreationForm(UserCreationForm):
    discord_id = forms.CharField(label="Discord Data")

    class Meta:
        model = DiscordPointingUser
        fields = ("discord_snowflake", "password1", "password2")

    def save(self, commit=True):
        discord_id = self.cleaned_data.get("discord_snowflake")
        password = self.cleaned_data.get("password1")
        user = DiscordPointingUser.objects.create_user(discord_snowflake=discord_id)
        user.set_password(self.cleaned_data.get("password"))
        if commit:
            user.save()

        return user
        # discord_id = get_or_create


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = DiscordPointingUser
        fields = ["discord_snowflake"]


# class SceneForm(forms.Form):
