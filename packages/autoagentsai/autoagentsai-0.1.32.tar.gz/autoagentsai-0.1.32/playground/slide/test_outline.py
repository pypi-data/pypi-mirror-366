import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from src.autoagentsai.slide import SlideAgent

def main():
    slide_agent = SlideAgent()
    
    file_path_list = ["docs/ai_report.pdf", "docs/industry_report.pdf"]
    # 基于文档生成大纲
    outline = slide_agent.outline(
        prompt="请生成一个关于AI技术发展的PPT大纲",
        file_path=file_path_list # optional
    )
    
    print(outline)


if __name__ == "__main__":
    main() 