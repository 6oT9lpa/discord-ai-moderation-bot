from typing import Any


def build_voice_lock_overwrites(channel: dict[str, Any], guild_id: int, locked: bool) -> list[dict[str, Any]]:
    overwrites = list(channel.get("permission_overwrites", []))
    everyone_id = str(guild_id)
    connect_bit = 0x00100000
    matched = False

    for overwrite in overwrites:
        if overwrite.get("id") == everyone_id and overwrite.get("type") == 0:
            allow = int(overwrite.get("allow", "0"))
            deny = int(overwrite.get("deny", "0"))
            if locked:
                deny |= connect_bit
                allow &= ~connect_bit
            else:
                allow |= connect_bit
                deny &= ~connect_bit
            overwrite["allow"] = str(allow)
            overwrite["deny"] = str(deny)
            matched = True
            break

    if not matched:
        overwrites.append(
            {
                "id": everyone_id,
                "type": 0,
                "allow": "0" if locked else str(connect_bit),
                "deny": str(connect_bit) if locked else "0",
            }
        )

    return overwrites
