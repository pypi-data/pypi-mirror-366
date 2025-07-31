import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.client.CrawlClient import CrawlClient, SiteConfig
from src.autoagentsai.client.ChatClient import ChatClient
from pydantic import BaseModel
from typing import List, Optional

def main():
    # 定义数据 Schema
    class Review(BaseModel):
        name: str
        city: str
        review: str
        date: Optional[str] = None  # 允许date为空

    class ReviewList(BaseModel):
        reviews: List[Review]

    chat_client = ChatClient(
        agent_id="7e46d18945fc49379063e3057a143c58",
        personal_auth_key="339859fa69934ea8b2b0ebd19d94d7f1",
        personal_auth_secret="93TsBecJplOawEipqAdF7TJ0g4IoBMtA",
        base_url="https://uat.agentspro.cn"
    )
    client = CrawlClient(chat_client)

    print("=" * 60)
    print("🧠 智能加载系统 - Trip.com 评论提取")
    print("🎯 目标：提取3件の口コミ（Trip.com评论）")
    print("=" * 60)

    # 方案一：使用自定义配置，指定期望数量
    custom_trip_config = SiteConfig(
        name="Trip.com智能加载版",
        selectors=[
            '[class*="review"]', 
            '[class*="comment"]',
            '[data-testid*="review"]',
            '.user-review',
            '.review-item'
        ],
        wait_time=3000,
        scroll_behavior=True,
        custom_actions=[
            {"action": "wait", "params": {"time": 3000}},
            {"action": "click_if_exists", "params": {"selectors": [
                'button:has-text("すべての口コミを表示")',
                'button:has-text("Show all reviews")',
                'a:has-text("すべての口コミを表示")',
                'a:has-text("Show all reviews")',
                'a:has-text("口コミを見る")',
                'a:has-text("レビューを見る")',
                '[data-testid*="show-all"]',
                '[data-testid*="read-all"]',
                '.show-all-reviews',
                '[class*="show-all"]',
                '[href*="review"]'
            ]}},
            {"action": "wait", "params": {"time": 4000}},
            {"action": "scroll", "params": {"direction": "bottom"}},
            {"action": "wait", "params": {"time": 2000}}
        ]
    )

    # 测试爬取
    result = client.scrape_url(
        url="https://travel.rakuten.co.jp/HOTEL/189204/189204.html",
        schema=ReviewList,
        prompt="Extract all reviews with name, city, review content, and date",
        formats=["extract"],
        custom_config=custom_trip_config
    )

    print(f"\n🏆 最终结果:")
    print(f"📊 提取的评论数量: {len(result['extract'].reviews)}")
    print(f"🎯 期望数量: 3")
    print(f"📈 成功率: {len(result['extract'].reviews)/3*100:.1f}%")

    # 显示前3个评论作为示例
    print(f"\n📝 评论示例 (前3个):")
    for i, review in enumerate(result['extract'].reviews[:3], 1):
        print(f"{i}. {review.name} ({review.city}): {review.review[:50]}...")

if __name__ == "__main__":
    main() 