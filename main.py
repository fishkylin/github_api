from dotenv import load_dotenv
from src.github_client.client import GitHubClient
load_dotenv()
client = GitHubClient()

print(client.list_repos("google"))