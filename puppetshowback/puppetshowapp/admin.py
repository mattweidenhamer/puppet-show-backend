from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Scene, Outfit, DiscordPointingUser
from .forms import *


@admin.register(DiscordPointingUser)
class CustomUserAdmin(BaseUserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = DiscordPointingUser
    date_hierarchy = "created_date"
    list_display = ("uuid", "discord_snowflake")
    list_filter = ("uuid", "discord_snowflake")

    ordering = ("created_date",)
    readonly_fields = ["uuid", "created_date"]
    filter_horizontal = ()
    fieldsets = (
        (
            "Information",
            {
                "fields": (
                    "uuid",
                    "discord_snowflake",
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_superuser",)},
        ),
    )
    add_fieldsets = ((None, {"fields": ("discord_snowflake",)}),)


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = (
        "scene_name",
        "scene_author",
        # "view_actors_link"
    )

    # def view_actors_link(self, obj):
    #     count = obj.actor_set.count()
    #     url = (
    #         reverse("admin:puppetshowapp_actor_changelist")
    #         + "?"
    #         + urlencode({"scene__id": f"{obj.id}"})
    #     )
    #     return format_html('<a href="{}">{} Actors</a>', url, count)
    #
    # view_actors_link.short_description = "Actors"

    fieldsets = [
        (
            "Scene Information",
            {"fields": ["scene_name", "scene_author"]},
        ),
    ]


@admin.register(Outfit)
class ActorAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Actor Information", {"fields": ["actor_base_user", "actor_hash", "scene"]}),
        (
            "Actor Gifs",
            {
                "fields": [
                    "speaking_animation",
                    "not_speaking_animation",
                    "sleeping_animation",
                    "connection_animation",
                    "disconnect_animation",
                ]
            },
        ),
    ]
