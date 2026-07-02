# 数据类：User, Repo, Issue...
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any


# 这里有疑问， from_dict 与各类中的 from_dict 是什么关系，以及 cls 和 return className 之间的用法关系
def from_dict(cls: type, data: dict[str, Any]) -> Any:
    field_names = {f.name for f in fields(cls)}
    filtered_data = {k: v for k, v in data.items() if k in field_names}
    return cls(**filtered_data)


@dataclass
class User:
    login: str
    id: int
    avatar_url: str = ""
    html_url: str = ""
    name: str | None = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    created_at: datetime | None = None

    @classmethod
    def from_dict(cls: type, data: dict[str, Any]) -> "User":
        return from_dict(cls, data)


@dataclass
class Repo:
    id: int
    name: str
    full_name: str  # "owner/name"
    description: str | None
    html_url: str
    language: str | None
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    topics: list[str]
    private: bool
    fork: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls: type, data: dict[str, Any]) -> "Repo":
        return from_dict(cls, data)


@dataclass
class Issue:
    id: int
    number: int
    title: str
    body: str | None
    state: str  # "open" | "closed"
    html_url: str
    user: User  # 嵌套 User
    labels: list[str]
    comments: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Issue":
        field_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in field_names}

        if "user" in filtered and isinstance(filtered["user"], dict):
            filtered["user"] = User.from_dict(filtered["user"])

        return cls(**filtered)


@dataclass
class IssueComment:
    id: int
    body: str
    user: User
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls: type, data: dict[str, Any]) -> "IssueComment":
        field_name = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in field_name}

        if "user" in filtered and isinstance(filtered["user"], dict):
            filtered["user"] = User.from_dict(filtered["user"])
        return cls(**filtered)


@dataclass
class Content:
    name: str
    path: str
    sha: str
    size: int
    content: str  # base64 编码的原始内容
    encoding: str  # "base64"
    download_url: str
    html_url: str

    @property
    def decoded_text(self) -> str:
        """自动 base64 解码为文本"""
        import base64

        return base64.b64decode(self.content).decode("utf-8")

    @classmethod
    def from_dict(cls: type, data: dict[str, Any]) -> "Content":
        return from_dict(cls, data)


@dataclass
class SearchResult:
    total_count: int
    incomplete_results: bool
    items: list[Repo]


@dataclass
class RateCategory:
    limit: int
    remaining: int
    reset: datetime
    used: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RateCategory":
        copied = data.copy()

        # 如果 reset 存在且是数字，转 datetime；否则保持 None
        reset_val = copied.get("reset")
        if isinstance(reset_val, (int, float)):
            copied["reset"] = datetime.fromtimestamp(reset_val, tz=timezone.utc)
        else:
            copied["reset"] = None  # 明确置为 None

        return from_dict(cls, copied)


@dataclass
class RateLimit:
    core: RateCategory
    search: RateCategory
