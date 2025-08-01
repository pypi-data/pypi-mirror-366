import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.graph import AutoWorkFlow


def main():
    auto_workflow = AutoWorkFlow()
    result = auto_workflow.build(prompt="帮我生成一个文档提问的智能体助手")
    print(result)


if __name__ == "__main__":
    main()