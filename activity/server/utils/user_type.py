from core.domain.activity_user_type import ActivityUserType


def resolve_user_type(access: dict[str, bool]) -> ActivityUserType:
    if access["is_admin"]:
        return ActivityUserType.ADMIN
    if access["is_developer"]:
        return ActivityUserType.DEVELOPER
    if access["is_streamer"]:
        return ActivityUserType.STREAMER
    return ActivityUserType.STANDARD
