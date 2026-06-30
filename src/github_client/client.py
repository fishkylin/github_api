# 核心类：请求、鉴权、重试
import requests
import os

from requests import Response
from .models import User

class GitHubClient:
    """GitHub REST API Client"""
    def __init__(self,
        token: str | None = None,
        base_url: str = "https://api.github.com",
        user_agent: str = "github-client/1.0",
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = base_url
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries

        self._session = requests.Session()
        self._session.headers.update(self._headers())

    def _headers(self) -> dict[str, str]:
        """构造请求头"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": self.user_agent,
            "X-GitHub-Api-Version": "2026-03-10",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str) -> Response:
        """鉴权 | 重试 | 错误处理"""
        resp = self._session.request(method, path)
        resp.raise_for_status()
        return resp

    def get_user(self, username: str) -> User:
        """根据 username 获取用户信息"""
        return User.from_dict(self._request("GET", f"{self.base_url}/users/{username}").json())

    def get_authenticated_user(self) -> User:
        """根据 token 获取用户信息"""
        return User.from_dict(self._request("GET", f"{self.base_url}/user").json())