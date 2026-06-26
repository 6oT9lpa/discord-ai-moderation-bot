from enum import Enum


class ActivityUserType(str, Enum):
    STANDARD = "standard"
    STREAMER = "streamer"
    DEVELOPER = "developer"
    ADMIN = "admin"
