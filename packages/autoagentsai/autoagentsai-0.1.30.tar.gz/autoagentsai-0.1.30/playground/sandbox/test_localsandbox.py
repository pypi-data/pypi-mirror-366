import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.sandbox import LocalSandboxService
from src.autoagentsai.client import ChatClient
from src.autoagentsai.utils.extractor import extract_python_code

def main():
    chat_client = ChatClient(
        agent_id="7e46d18945fc49379063e3057a143c58",
        personal_auth_key="339859fa69934ea8b2b0ebd19d94d7f1",
        personal_auth_secret="93TsBecJplOawEipqAdF7TJ0g4IoBMtA",
        base_url="https://uat.agentspro.cn"
    )

    content = ""
    for event in chat_client.invoke("帮我生成一段python代码，一个简单的matplotlib图表，并保存为图片"):
        if event['type'] == 'token':
            content += event['content']
            
    ai_generated_code = extract_python_code(content)

    sandbox = LocalSandboxService()
    execution_result = sandbox.run_code(ai_generated_code)
    print(execution_result)

if __name__ == "__main__":
    main()