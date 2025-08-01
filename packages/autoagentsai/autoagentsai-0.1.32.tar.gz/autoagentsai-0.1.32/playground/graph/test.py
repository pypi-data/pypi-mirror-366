import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.graph import FlowGraph


def main():
    graph = FlowGraph(
            personal_auth_key="7217394b7d3e4becab017447adeac239",
            personal_auth_secret="f4Ziua6B0NexIMBGj1tQEVpe62EhkCWB",
            base_url="https://uat.agentspro.cn"
        )

    # 添加节点
    graph.add_node(
        node_id="question1",
        module_type="questionInput",
        position={"x": 0, "y": 300},
        inputs={
            "inputText": True,
            "uploadFile": True,
            "uploadPicture": False,
            "fileContrast": False,
            "initialInput": True
        }
    )

    graph.add_node(
        node_id="pdf2md1",
        module_type="pdf2md",
        position={"x": 500, "y": 300},
        inputs={
            "pdf2mdType": "deep_pdf2md"
        }
    )

    graph.add_node(
        node_id="ai1",
        module_type="aiChat",
        position={"x": 1000, "y": 300},
        inputs={
            "model": "glm-4-airx",
            "quotePrompt": "你是一个专业文档助手，请根据以下文档内容回答问题：\n帮我生成一个文档提问的智能体助手",
            "knSearch": "",
            "temperature": 0.1
        }
    )

    memory_variable_inputs = []
    input_1 = {
        "key": "test1",
        "value_type": "String"
    }
    input_2 = {
        "key": "question1",
        "value_type": "Boolean"
    }

    memory_variable_inputs.append(input_1)
    memory_variable_inputs.append(input_2)

    graph.add_node(
        node_id="addMemoryVariable1",
        module_type="addMemoryVariable",
        position={"x": 1500, "y": 300},
        inputs=memory_variable_inputs
    )

    graph.add_node(
        node_id="confirmreply1",
        module_type="confirmreply",
        position={"x": 2000, "y": 300},
        inputs={
            "text": "",
            "stream": True
        }
    )

    # 添加连接边
    graph.add_edge("question1", "pdf2md1", "finish", "switchAny")
    graph.add_edge("question1", "pdf2md1", "files", "files")

    graph.add_edge("pdf2md1", "ai1", "finish", "switchAny")
    graph.add_edge("pdf2md1", "ai1", "pdf2mdResult", "text")

    graph.add_edge("pdf2md1", "addMemoryVariable1", "pdf2mdResult", "question1")
    graph.add_edge("ai1", "addMemoryVariable1", "answerText", "test1")

    graph.add_edge("ai1", "confirmreply1", "finish", "switchAny")

    # print(graph.to_json())

    graph.compile(
            intro="这是一个专业的文档助手，可以帮助用户分析和理解文档内容",
            category="文档处理",
            prologue="你好！我是你的文档助手，请上传文档，我将帮您分析内容。",
            shareAble=True,
            allowVoiceInput=False,
            autoSendVoice=False
        )

if __name__ == "__main__":
    main()