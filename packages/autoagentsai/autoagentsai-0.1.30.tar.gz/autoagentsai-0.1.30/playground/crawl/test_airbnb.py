import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.client import CrawlClient, ChatClient
from pydantic import BaseModel
from typing import List, Optional

def main():
    # 定义数据 Schema
    class Review(BaseModel):
        name: str
        city: str
        review: str
        date: Optional[str] = None

    class ReviewList(BaseModel):
        reviews: List[Review]

    chat_client = ChatClient(
            agent_id="7e46d18945fc49379063e3057a143c58",
            personal_auth_key="339859fa69934ea8b2b0ebd19d94d7f1",
            personal_auth_secret="93TsBecJplOawEipqAdF7TJ0g4IoBMtA",
            base_url="https://uat.agentspro.cn"
        )
    client = CrawlClient(chat_client)

    # 调用爬取 + LLM Schema 抽取
    result = client.scrape_url(
        url="https://www.airbnb.jp/rooms/958960293702074652/reviews?source_impression_id=p3_1753601479_P3IRdqCiBNMUEIyi",
        schema=ReviewList,
        prompt="Extract reviews with name, city, review, and date",
        formats=["extract", "html"]
    )

    print(result["extract"])


if __name__ == "__main__":
    main()
