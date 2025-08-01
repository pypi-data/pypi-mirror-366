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
        node_id="confirmreply1",
        module_type="confirmreply",
        position={"x": 1000, "y": 300},
        inputs={
            "text": r"文件内容：{{pdf2md1_pdf2mdResult}}",
            "stream": True
        }
    )

    graph.add_node(
        node_id="ai1",
        module_type="aiChat",
        position={"x": 1500, "y": 300},
        inputs={
            "model": "glm-4-airx",
            "quotePrompt": """
<角色>
你是一个文件解答助手，你可以根据文件内容，解答用户的问题
</角色>

<文件内容>
{{pdf2md1_pdf2mdResult}}
</文件内容>

<用户问题>
{{question1_userChatInput}}
</用户问题>
            """,
            "knSearch": "",
            "temperature": 0.1
        }
    )

    memory_variable_inputs = []
    question1_userChatInput = {
        "key": "question1_userChatInput",
        "value_type": "String"
    }
    pdf2md1_pdf2mdResult = {
        "key": "pdf2md1_pdf2mdResult",
        "value_type": "String"
    }
    ai1_answerText = {
        "key": "ai1_answerText",
        "value_type": "String"
    }
    
    memory_variable_inputs.append(question1_userChatInput)
    memory_variable_inputs.append(pdf2md1_pdf2mdResult)
    memory_variable_inputs.append(ai1_answerText)

    graph.add_node(
        node_id="addMemoryVariable1",
        module_type="addMemoryVariable",
        position={"x": 0, "y": 1500},
        inputs=memory_variable_inputs
    )


    # 添加连接边
    graph.add_edge("question1", "pdf2md1", "finish", "switchAny")
    graph.add_edge("question1", "pdf2md1", "files", "files")
    graph.add_edge("question1", "addMemoryVariable1", "userChatInput", "question1_userChatInput")

    graph.add_edge("pdf2md1", "confirmreply1", "finish", "switchAny")
    graph.add_edge("pdf2md1", "addMemoryVariable1", "pdf2mdResult", "pdf2md1_pdf2mdResult")
    
    graph.add_edge("confirmreply1", "ai1", "finish", "switchAny")

    graph.add_edge("ai1", "addMemoryVariable1", "answerText", "ai1_answerText")

    
    # 编译
    graph.compile(
            name="awf-beta-文档助手",
            intro="这是一个专业的文档助手，可以帮助用户分析和理解文档内容",
            category="文档处理",
            prologue="你好！我是你的文档助手，请上传文档，我将帮您分析内容。",
            shareAble=True,
            allowVoiceInput=False,
            autoSendVoice=False
        )

if __name__ == "__main__":
    main()