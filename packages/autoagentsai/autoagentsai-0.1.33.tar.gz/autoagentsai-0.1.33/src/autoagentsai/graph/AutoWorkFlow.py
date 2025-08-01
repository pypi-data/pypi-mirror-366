from typing import Optional
\
from autoagentsai.client import ChatClient
from autoagentsai.utils.extractor import extract_python_code
from autoagentsai.sandbox import LocalSandboxService
from autoagentsai.graph import FlowGraph


class AutoWorkFlow:

    def __init__(self):
        self.client = ChatClient(
            agent_id="312ed7c93c1d4d7c881bb1b4e4c1e61d",
            personal_auth_key="7217394b7d3e4becab017447adeac239",
            personal_auth_secret="f4Ziua6B0NexIMBGj1tQEVpe62EhkCWB",
            base_url="https://uat.agentspro.cn"
        )
        self.sandbox = LocalSandboxService()

    def build(self, prompt: str, file_path_list: Optional[list[str]] = None, image_path_list: Optional[list[str]] = None, **kwargs):
        content = ""
        for event in self.client.invoke(prompt, files=file_path_list, images=image_path_list):
            if event["type"] == "token":
                content += event["content"]
                print(event["content"], end="", flush=True)
            elif event["type"] == "reasoning_token":
                print(event["content"], end="", flush=True)

        content = extract_python_code(content)

        result = self.sandbox.run_code(str(content))
        return result