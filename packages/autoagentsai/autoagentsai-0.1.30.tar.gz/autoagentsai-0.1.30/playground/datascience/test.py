import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.datascience import DSAgent


def main():
    ds_agent = DSAgent()
    result = ds_agent.analyze_csv(
        user_query="请帮我进行数据分析", 
        file_path="playground/test_workspace/data.csv",
        verbose=True
    )
    print(result)

if __name__ == "__main__":
    main()