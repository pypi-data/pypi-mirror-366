import os
import sys

# 将 `src` 目录添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.graph.FlowGraph import FlowGraph
from src.autoagentsai.types import CreateAppParams


def main():
    graph = FlowGraph()

    # 添加节点
    graph.add_node(
        node_id="question1",
        module_type="questionInput",
        position={"x": 300, "y": 100},
        inputs=[
            {"key": "inputText", "value": True},
            {"key": "uploadFile", "value": True},
            {"key": "uploadPicture", "value": False},
            {"key": "fileContrast", "value": False},
            {"key": "initialInput", "value": True}
        ]
    )

    graph.add_node(
        node_id="pdf2md1",
        module_type="pdf2md",
        position={"x": 600, "y": 100},
        inputs=[{"key": "pdf2mdType", "value": "deep_pdf2md"}]
    )

    graph.add_node(
        node_id="ai1",
        module_type="aiChat",
        position={"x": 900, "y": 100},
        inputs=[
            {"key": "model", "value": "glm-4-airx"},
            {"key": "quotePrompt", "value": "你是一个专业文档助手，请根据以下文档内容回答问题：\n{{text}}"},
            {"key": "knSearch", "value": ""},
            {"key": "temperature", "value": 0.1}
        ]
    )
    memory_variable_inputs = []
    memory_variable_inputs.append({"key": "{question}", "value": "{{answerText}}"})

    graph.add_node(
        node_id="addMemoryVariable1",
        module_type="addMemoryVariable",
        position={"x": 1200, "y": 100},
        inputs=[{"key": "{question}", "value": "{{answerText}}"}]
    )

    graph.add_node(
        node_id="confirmreply1",
        module_type="confirmreply",
        position={"x": 1500, "y": 100},
        inputs=[
            {"key": "text", "value": "{{answerText}}"},
            {"key": "stream", "value": True}
        ]
    )

    # 添加连接边
    graph.add_edge("question1", "pdf2md1", "finish", "switchAny")
    graph.add_edge("question1", "pdf2md1", "files", "files")

    graph.add_edge("pdf2md1", "ai1", "finish", "switchAny")
    graph.add_edge("pdf2md1", "ai1", "pdf2mdResult", "text")

    graph.add_edge("ai1", "addMemoryVariable1", "answerText", "question")
    graph.add_edge("ai1", "confirmreply1", "finish", "switchAny")

    print(graph.to_json())

    graph.compile(CreateAppParams())

if __name__ == "__main__":
    main()