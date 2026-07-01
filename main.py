from dotenv import load_dotenv
from src.github_client.client import GitHubClient
load_dotenv()
client = GitHubClient()
i = 1   
for issue in client.list_issues("python", "cpython", state="all", max_items=1):
    print(f"i -- #{issue.number} {issue.title} [{issue.state}]")
    i += 1