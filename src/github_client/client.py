# 核心类：请求、鉴权、重试
import requests
import os

from typing import Iterator
from requests import Response
from .models import (
    User,
    Repo,
    Issue,
    IssueComment,
    Content,
    SearchResult,
    RateLimit,
    RateCategory,
)


class GitHubClient:
    """GitHub REST API Client"""

    def __init__(
        self,
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

    # ==================== Private ====================
    def _headers(self) -> dict[str, str]:
        """构造请求头"""
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": self.user_agent,
            "X-GitHub-Api-Version": "2026-03-10",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        json: dict | None = None,
        data: dict | None = None,
    ) -> Response:
        """鉴权 | 重试 | 错误处理"""
        resp = self._session.request(
            method,
            url=f"{self.base_url}/{url}",
            params=params,
            json=json,
            data=data,
        )
        resp.raise_for_status()
        return resp

    def _paginated(
        self,
        cls: type,
        url: str,
        per_page: int,
        params: dict | None = None,
        max_items: int | None = None,
    ) -> Iterator:
        page = 1
        yielded = 0
        request_params = {"per_page": per_page, "page": page}
        if params:
            request_params.update(params)
        while True:
            reps = self._request(
                method="GET",
                url=url,
                params=request_params,
            )
            print(reps.url)
            data = reps.json()

            if not data:
                break

            for item in data:
                yield cls.from_dict(item)
                yielded += 1
                if max_items and yielded >= max_items:
                    return
            if len(data) < per_page:
                break
            page += 1

    # ==================== User ====================

    def get_user(self, username: str) -> User:
        """根据 username 获取用户信息"""
        return User.from_dict(self._request("GET", f"users/{username}").json())

    def get_authenticated_user(self) -> User:
        """根据 token 获取用户信息"""
        return User.from_dict(self._request("GET", "user").json())

    # ==================== Repositories ====================

    def list_repos(
        self,
        username: str | None = None,
        per_page: int = 30,
        max_items: int | None = None,
    ) -> Iterator[Repo]:
        """根据 Token 或 username 获取用户仓库列表，支持分页"""
        url = "user/repos" if username is None else f"users/{username}/repos"
        return self._paginated(
            cls=Repo, url=url, per_page=per_page, max_items=max_items
        )

    def get_repo(self, owner: str, repo: str) -> Repo:
        """获取指定用户仓库的信息"""
        return Repo.from_dict(self._request("GET", f"repos/{owner}/{repo}").json())

    def create_repo(self, name: str, private: bool = True) -> Repo:
        data = {
            "name": name,
            "private": private,
        }
        return Repo.from_dict(self._request("POST", "user/repos", json=data).json())

    def star_preo(self, owner: str, repo: str) -> None:
        """使用当前 Token 用户为指定用户仓库点亮星星"""
        self._request("PUT", f"user/starred/{owner}/{repo}")

    def unstar_preo(self, owner: str, repo: str) -> None:
        """使用当前 Token 用户为指定用户仓库取消星星"""
        self._request("DELETE", f"user/starred/{owner}/{repo}")

    # ==================== Issue ====================

    def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 30,
        max_items: int | None = None,
        labels: list[str] | None = None,
    ) -> Iterator[Issue]:
        params = {
            "state": state,
            "per_page": per_page,
            "labels": labels,
        }
        return self._paginated(
            cls=Issue,
            url=f"repos/{owner}/{repo}/issues",
            params=params,
            max_items=max_items,
            per_page=per_page,
        )

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
    ) -> Issue:
        """创建 Issue"""
        resp = self._request(
            method="POST",
            url=f"repos/{owner}/{repo}/issues",
            json={
                "owner": owner,
                "repo": repo,
                "title": title,
                "body": body,
                "labels": labels,
            },
        )
        data = resp.json()
        return Issue.from_dict(data)

    def create_comment(
        self, owner: str, repo: str, issue_number: int, body: str
    ) -> IssueComment:
        resp = self._request(
            method="POST",
            url=f"repos/{owner}/{repo}/issues/{issue_number}/comments",
            json={
                "owner": owner,
                "repo": repo,
                "body": body,
            },
        )
        data = resp.json()
        return IssueComment.from_dict(data)

    # ==================== Content ====================

    def get_content(
        self, owner: str, repo: str, path: str, ref: str | None = None
    ) -> Content:
        return Content.from_dict(
            self._request(
                method="GET",
                url=f"repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref},
            ).json()
        )

    # ==================== Search ====================
    # get /search/issues
    def search_repos(
        self,
        query: str,
        sort: str | None = None,
        order: str | None = None,
        per_page: int = 30,
    ) -> SearchResult:
        params = {"per_page": per_page, "q": query, "sort": sort, "order": order}
        reps = self._request(method="GET", url="search/repositories", params=params)
        data = reps.json()
        repos = [Repo.from_dict(item) for item in data.get("items", [])]
        return SearchResult(
            total_count=data.get("total_count", 0),
            incomplete_results=data.get("incomplete_results", False),
            items=repos,
        )

    # ==================== RateLimit ====================

    def get_rate_limit(self) -> RateLimit:
        reps = self._request(
            method="GET",
            url="rate_limit",
        )
        data = reps.json()
        resources = data["resources"]
        return RateLimit(
            core=RateCategory.from_dict(resources.get("core", {})),
            search=RateCategory.from_dict(resources.get("search", {})),
        )
