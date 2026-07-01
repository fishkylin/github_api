# 数据类：User, Repo, Issue...
from dataclasses import dataclass, fields
from datetime import datetime
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
    full_name: str          # "owner/name"
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
    state: str              # "open" | "closed"
    html_url: str
    user: User              # 嵌套 User
    labels: list[str]
    comments: int
    created_at: datetime
    updated_at: datetime

    @classmethod    
    def from_dict(cls, data: dict[str, Any]) -> "Issue":
        # 先把顶层的普通字段过滤出来
        field_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in field_names}
        
        if "user" in filtered and isinstance(filtered["user"], dict):
            filtered["user"] = User.from_dict(filtered["user"])
            
        return cls(**filtered)