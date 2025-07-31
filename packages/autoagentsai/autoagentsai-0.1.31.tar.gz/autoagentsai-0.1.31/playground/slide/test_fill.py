import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from src.autoagentsai.slide import SlideAgent

def main():
    prompt = "请根据以下数据生成一个PPT，数据如下："
    file_path_list = ["playground/test_workspace/data.csv"]
    
    ppt_agent = SlideAgent()
    ppt_agent.outline(prompt, file_path_list)


if __name__ == "__main__":
    main() 