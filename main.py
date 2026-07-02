from dotenv import load_dotenv
from src.github_client.client import GitHubClient

load_dotenv()
client = GitHubClient()
rate = client.get_rate_limit()
print(f"剩余: {rate.core.remaining}/{rate.core.limit}")
print(f"重置时间: {rate.core.reset}")  # datetime
