from enum import Enum


class ServerRolePurpose(str, Enum):
    ACTIVITY_ADMIN = "activity_admin"
    ACTIVITY_STREAMER = "activity_streamer"
    ACTIVITY_DEVELOPER = "activity_developer"

    @classmethod
    def activity_member_purposes(cls) -> tuple["ServerRolePurpose", ...]:
        return (
            cls.ACTIVITY_STREAMER,
            cls.ACTIVITY_DEVELOPER,
        )
