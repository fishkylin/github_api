# 数据类：User, Repo, Issue...
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any

def from_dict(cls: type, data: dict[str, Any]):
    field_names = {f.name for f in fields(cls)}
    filtered_data = {k: v for k, v in data.items() if k in field_names}
    return cls(**filtered_data)

@dataclass
class User:
    login = str,
    id = int,
    name: str | None
    avatar_url: str
    html_url: str
    public_repos: int
    followers: int
    following: int
    created_at: datetime

    @classmethod
    def from_dict(cls: type, data: dict[str, Any]) -> "User":
        return from_dict(cls, data)