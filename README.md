# GitHub API Client

A lightweight Python client for the GitHub REST API with support for authentication, pagination, and common GitHub operations.

## Features

- 🔐 Token-based authentication
- 📄 User management (get user info, authenticated user)
- 📦 Repository operations (list, get, create, star/unstar)
- 🐛 Issue management (list issues with filtering)
- 🔄 Automatic pagination support
- ⚡ Configurable retries and timeouts
- 📝 Type-safe with Pydantic models

## Installation

Install the package using `uv`:

```bash
uv add github-api
```

Or with pip:

```bash
pip install github-api
```

## Setup

### Authentication

Create a `.env` file in your project root with your GitHub token:

```env
GITHUB_TOKEN=your_github_token_here
```

Or pass the token directly to the client:

```python
from src.github_client.client import GitHubClient

client = GitHubClient(token="your_token_here")
```

## Usage Examples

### Initialize the Client

```python
from src.github_client.client import GitHubClient

# Using token from environment variable
client = GitHubClient()

# Or with explicit token
client = GitHubClient(token="ghp_xxxxxxxxxxxxx")

# With custom configuration
client = GitHubClient(
    token="ghp_xxxxxxxxxxxxx",
    base_url="https://api.github.com",
    timeout=30,
    max_retries=3
)
```

### User Operations

#### Get User Information

```python
# Get information about a specific user
user = client.get_user("torvalds")
print(f"User: {user.login}")
print(f"Followers: {user.followers}")
print(f"Public Repos: {user.public_repos}")
```

#### Get Authenticated User

```python
# Get information about the authenticated user (requires token)
me = client.get_authenticated_user()
print(f"Hello, {me.login}!")
print(f"Name: {me.name}")
print(f"Following: {me.following}")
```

### Repository Operations

#### List User Repositories

```python
# List repositories for a specific user
for repo in client.list_repos(username="torvalds", per_page=10):
    print(f"{repo.full_name}: {repo.stargazers_count} ⭐")

# List your own repositories (requires authentication)
for repo in client.list_repos(per_page=10):
    print(f"{repo.name} - {repo.description}")

# Limit the number of results
for repo in client.list_repos(username="facebook", max_items=5):
    print(f"{repo.name}")
```

#### Get Repository Details

```python
# Get detailed information about a repository
repo = client.get_repo("torvalds", "linux")
print(f"Repository: {repo.name}")
print(f"Stars: {repo.stargazers_count}")
print(f"Forks: {repo.forks_count}")
print(f"Language: {repo.language}")
print(f"URL: {repo.html_url}")
```

#### Create a New Repository

```python
# Create a private repository
repo = client.create_repo("my-new-project", private=True)
print(f"Created repository: {repo.full_name}")

# Create a public repository
repo = client.create_repo("my-public-project", private=False)
print(f"Created repository: {repo.full_name}")
```

#### Star/Unstar Repositories

```python
# Star a repository
client.star_preo("python", "cpython")
print("Repository starred!")

# Unstar a repository
client.unstar_preo("python", "cpython")
print("Repository unstarred!")
```

### Issue Operations

#### List Issues

```python
# List open issues in a repository
for issue in client.list_issues("python", "cpython", state="open", max_items=10):
    print(f"#{issue.number}: {issue.title}")
    print(f"  Author: {issue.user.login}")
    print(f"  Comments: {issue.comments}")
    print()

# List closed issues
for issue in client.list_issues("python", "cpython", state="closed", max_items=5):
    print(f"#{issue.number}: {issue.title} [CLOSED]")

# List all issues
for issue in client.list_issues("python", "cpython", state="all", per_page=50):
    print(f"#{issue.number}: {issue.title} [{issue.state}]")

# Filter by labels
for issue in client.list_issues(
    "python", 
    "cpython", 
    state="open",
    labels=["bug", "priority-high"],
    max_items=20
):
    print(f"#{issue.number}: {issue.title}")
    print(f"  Labels: {issue.labels}")
```

## Data Models

### User

```python
@dataclass
class User:
    login: str                      # GitHub username
    id: int                         # User ID
    avatar_url: str                 # URL to avatar image
    html_url: str                   # URL to user profile
    name: str | None                # Display name
    public_repos: int               # Number of public repositories
    followers: int                  # Number of followers
    following: int                  # Number of users following
    created_at: datetime | None     # Account creation date
```

### Repo

```python
@dataclass
class Repo:
    id: int                         # Repository ID
    name: str                       # Repository name
    full_name: str                  # "owner/name" format
    description: str | None         # Repository description
    html_url: str                   # URL to repository
    language: str | None            # Primary programming language
    stargazers_count: int           # Number of stars
    forks_count: int                # Number of forks
    open_issues_count: int          # Number of open issues
    topics: list[str]               # Repository topics/tags
    private: bool                   # Whether repository is private
    fork: bool                      # Whether repository is a fork
    created_at: datetime            # Repository creation date
    updated_at: datetime            # Last update date
```

### Issue

```python
@dataclass
class Issue:
    id: int                         # Issue ID
    number: int                     # Issue number
    title: str                      # Issue title
    body: str | None                # Issue description
    state: str                      # "open" or "closed"
    html_url: str                   # URL to issue
    user: User                      # Issue creator
    labels: list[str]               # Issue labels
    comments: int                   # Number of comments
    created_at: datetime            # Creation date
    updated_at: datetime            # Last update date
```

## Configuration Options

### GitHubClient Parameters

- **token** (`str | None`): GitHub personal access token. If not provided, reads from `GITHUB_TOKEN` environment variable.
- **base_url** (`str`): Base URL for GitHub API (default: `https://api.github.com`)
- **user_agent** (`str`): User agent string (default: `github-client/1.0`)
- **timeout** (`int`): Request timeout in seconds (default: `30`)
- **max_retries** (`int`): Maximum number of retries for failed requests (default: `3`)

## Error Handling

The client will raise exceptions from the `requests` library if API requests fail:

```python
from requests.exceptions import HTTPError

try:
    user = client.get_user("nonexistent-user-xyz")
except HTTPError as e:
    print(f"Error: {e.response.status_code} - {e.response.text}")
```

## Pagination

The client automatically handles pagination for list operations:

```python
# Iterate through all results (handles pagination automatically)
for issue in client.list_issues("python", "cpython", state="open"):
    print(f"#{issue.number}: {issue.title}")

# Limit results with max_items
for issue in client.list_issues("python", "cpython", state="open", max_items=100):
    print(f"#{issue.number}: {issue.title}")

# Control page size
for issue in client.list_issues("python", "cpython", state="open", per_page=50):
    print(f"#{issue.number}: {issue.title}")
```

## Requirements

- Python >= 3.13
- requests >= 2.34.2
- pydantic >= 2.13.4
- pydantic-settings >= 2.14.2
- python-dotenv >= 1.2.2

## License

This project is open source and available under the MIT License.
