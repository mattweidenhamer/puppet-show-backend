from rest_framework import serializers
from .models.configuration_models import Outfit, Scene
from .models.authentication_models import DiscordPointingUser
from .models.data_models import Animation, LogFile
from .models.new_models import Performer


# class DiscordDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DiscordData
#         fields = ("user_snowflake", "user_username", "profile_picture")
#         read_only_field = ["user_username", "profile_picture"]


class AnimationSerializer(serializers.ModelSerializer):
    outfit_identifier = serializers.CharField(write_only=True)

    class Meta:
        model = Animation
        fields = ("animation_type", "animation_path", "outfit_identifier", "identifier")

    def create(self, validated_data):
        if "outfit_identifier" not in validated_data:
            raise serializers.ValidationError(
                f"outfit_identifier is required to create an animation, provided data was {validated_data}"
            )
        outfit_id_clean = validated_data.pop("outfit_identifier")
        try:
            outfit = Outfit.objects.get(identifier=outfit_id_clean)
        except Outfit.DoesNotExist:
            raise serializers.ValidationError(
                f"outfit_identifier {outfit_id_clean} does not exist and needs to be added first."
            )
        validated_data["outfit"] = outfit
        animation = Animation.objects.create(**validated_data)
        return animation


class OutfitSerializer(serializers.ModelSerializer):
    animations = AnimationSerializer(many=True, required=False, read_only=True)
    performer_id = serializers.CharField(write_only=True)

    class Meta:
        model = Outfit
        fields = (
            "performer",
            "outfit_name",
            "animations",
            "scene",
            "settings",
            "performer_id",
            "identifier",
        )
        read_only_fields = ["performer", "scene"]

        extra_kwargs = {
            "scene": {"required": False},
            "performer": {"required": False},
        }

    def create(self, validated_data):
        if "performer_id" not in validated_data:
            raise serializers.ValidationError(
                f"performer_id is required to create an outfit, provided data was {validated_data}"
            )
        performer_id_clean = validated_data.pop("performer_id")
        try:
            performer = Performer.objects.get(identifier=performer_id_clean)
        except Performer.DoesNotExist:
            raise serializers.ValidationError(
                f"performer_id {performer_id_clean} does not exist and needs to be added first."
            )
        validated_data["performer"] = performer
        outfit = Outfit.objects.create(**validated_data)
        return outfit


class OutfitSerializerNoScene(OutfitSerializer):
    class Meta:
        model = Outfit
        fields = (
            "performer",
            "outfit_name",
            "animations",
            "settings",
            "performer_id",
            "identifier",
        )
        read_only_fields = ["performer"]

        extra_kwargs = {
            "performer": {"required": False},
        }


class OutfitSerializerForPerformer(serializers.ModelSerializer):
    animations = AnimationSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Outfit
        fields = (
            "outfit_name",
            "animations",
            "settings",
            "identifier",
        )
        read_only_fields = ["outfit_name", "animations", "settings", "identifier"]


# class ActorSerializerStage(serializers.ModelSerializer):
#     animations = AnimationSerializer(many=True, required=False)
#     baseUser = serializers.ReadOnlyField(source="actor_base_user.user_snowflake")

#     class Meta:
#         model = Outfit
#         fields = (
#             "actor_name",
#             "identifier",
#             "settings",
#             "animations",
#             "baseUser",
#             "settings",
#         )
#         read_only_field = [
#             "actor_name",
#             "animations",
#             "baseUser",
#             "identifier",
#             "settings",
#         ]


class SceneSerializer(serializers.ModelSerializer):
    outfits = OutfitSerializerNoScene(many=True, required=False)

    class Meta:
        model = Scene
        fields = (
            "scene_name",
            "scene_settings",
            "is_active",
            "outfits",
            "identifier",
            "scene_author",
        )
        read_only_fields = ["scene_author", "is_active"]


class PerformerSerializer(serializers.ModelSerializer):
    parent_user_snowflake = serializers.CharField(
        source="parent_user.discord_snowflake", read_only=True
    )

    class Meta:
        model = Performer
        fields = (
            "identifier",
            "discord_snowflake",
            "discord_username",
            "parent_user_snowflake",
            "discord_avatar",
            "settings",
        )
        read_only_fields = ["identifier", "discord_username", "discord_avatar"]

    def create(self, validated_data):
        new_performer = super().create(validated_data)
        new_performer.request_update_user_info()
        return new_performer


class StageSerializer(serializers.ModelSerializer):
    get_outfit = OutfitSerializerForPerformer(read_only=True)

    class Meta:
        model = Performer
        fields = (
            "identifier",
            "discord_snowflake",
            "discord_avatar",
            "get_outfit",
            "settings",
        )
        read_only_fields = [
            "identifier",
            "discord_username",
            "discord_avatar",
            "get_outfit",
            "settings",
        ]


# TODO: Considier making this more succinct so tha the user's active scene isn't called twice.
class UserSerializer(serializers.ModelSerializer):
    scenes = SceneSerializer(many=True, required=False, read_only=True)
    performers = PerformerSerializer(many=True, required=False, read_only=True)
    active_scene = SceneSerializer(required=False, read_only=True)

    class Meta:
        model = DiscordPointingUser
        fields = [
            "uuid",
            "discord_snowflake",
            "discord_username",
            "scenes",
            "active_scene",
            "performers",
            "discord_avatar",
            "added_performers_count",
        ]
        read_only_fields = ["uuid", "discord_snowflake", "added_performer_count"]


class LogReceiver(serializers.ModelSerializer):
    class Meta:
        model = LogFile
        fields = ["log_type", "log_file"]

    def save(self, *args, **kwargs):
        log_file = self.validated_data["log_file"]
        log_type = self.validated_data["log_type"]
        new_log = LogFile(log_type=log_type, log_file=log_file)
        new_log.save()
        return new_log
