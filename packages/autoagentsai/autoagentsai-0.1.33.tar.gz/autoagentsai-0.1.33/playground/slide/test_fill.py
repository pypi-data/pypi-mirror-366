import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from src.autoagentsai.slide import SlideAgent

def main():
    template_path = "playground/test_workspace/page.pptx"
    output_path = "playground/test_workspace/output_new_format_test.pptx"
    test_data = {
        "page": [
            { 
                "page_number": 1,
                "title": "智能排班系统",
                "subtitle": "提升工作效率的解决方案",
                "logo": "company_logo.png"
            },
            { 
                "page_number": 2,
                "title": "核心需求",
                "sections": [
                    { "title": "精准计算", "content": "基于AI算法的精确计算，确保排班公平性和效率" },
                    { "title": "自动排班", "content": "智能化排班系统，减少人工干预，提高管理效率" }
                ]
            },
            {
                "page_number": 3,
                "title": "系统架构",
                "table": "playground/test_workspace/data.csv"
            },
            {
                "page_number": 4,
                "title": "商品列表",
                "table": [
                    {
                        "count": 4,
                        "name": "**高级墙纸**",
                        "desc": "* 书房专用\n* 卧室适配\n* `防水材质`",
                        "discount": 1500,
                        "tax": 27,
                        "price": 400,
                        "totalPrice": 1600,
                        "picture": "globe.png"
                    },
                    {
                        "count": 2,
                        "name": "*经典地板*",
                        "desc": "* 客厅铺设\n* **耐磨**材质\n* `环保认证`",
                        "discount": 800,
                        "tax": 15,
                        "price": 600,
                        "totalPrice": 1200,
                        "picture": "floor.png"
                    }
                ]
            }
        ]
    }
    
    ppt_agent = SlideAgent()
    ppt_agent.fill(test_data, template_path, output_path)


if __name__ == "__main__":
    main() 