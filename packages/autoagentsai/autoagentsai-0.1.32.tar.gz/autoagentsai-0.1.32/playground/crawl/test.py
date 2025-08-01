import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.client.CrawlClient import CrawlClient
from src.autoagentsai.client import ChatClient
from pydantic import BaseModel
from typing import List

def main():
    # 定义数据 Schema
    class Repository(BaseModel):
        name: str
        description: str
        url: str
        stars: int

    class RepoList(BaseModel):
        repos: List[Repository]

    chat_client = ChatClient(
            agent_id="7e46d18945fc49379063e3057a143c58",
            personal_auth_key="339859fa69934ea8b2b0ebd19d94d7f1",
            personal_auth_secret="93TsBecJplOawEipqAdF7TJ0g4IoBMtA",
            base_url="https://uat.agentspro.cn"
        )
    client = CrawlClient(chat_client)

    # 调用爬取 + LLM Schema 抽取
    result = client.scrape_url(
        url="https://github.com/trending",
        schema=RepoList,
        prompt="Extract trending repositories with name, description, url, and stars",
        formats=["extract", "html"]
    )

    print(result["extract"])


if __name__ == "__main__":
    main()
