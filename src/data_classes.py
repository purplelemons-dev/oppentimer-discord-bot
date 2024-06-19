from typing import TypedDict


class UserInfo(TypedDict):
    messageCount: int

class ReactionRoles(TypedDict):
    message_id: int

    roles: dict[str, int]
    "emoji: role_id"

__all__ = ["UserInfo", "ReactionRoles"]
