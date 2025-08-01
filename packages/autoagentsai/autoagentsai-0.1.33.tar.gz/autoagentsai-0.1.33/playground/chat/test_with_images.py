import os
import sys

# 自动添加项目根目录到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.client import ChatClient

client = ChatClient(
    agent_id="c41e34e3e0bb4ea9a5380b7b06861e5c",
    personal_auth_key="339859fa69934ea8b2b0ebd19d94d7f1",
    personal_auth_secret="93TsBecJplOawEipqAdF7TJ0g4IoBMtA"
)

# 图片列表，支持本地图片和网络图片
image_path_list = [
    "playground/test_workspace/img/1.jpeg",
    "https://plus.unsplash.com/premium_photo-1750116257648-64c9c39dbd8d?q=80&w=2340&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
]

for event in client.invoke(prompt="请分析这两张图片", images=image_path_list):
    if event['type'] == 'start_bubble':
        print(f"\n{'=' * 20} 消息气泡{event['bubble_id']}开始 {'=' * 20}")
    elif event['type'] == 'reasoning_token':
        print(event['content'], end='', flush=True)
    elif event['type'] == 'token':
        print(event['content'], end='', flush=True)
    elif event['type'] == 'end_bubble':
        print(f"\n{'=' * 20} 消息气泡结束 {'=' * 20}")
    elif event['type'] == 'finish':
        print(f"\n{'=' * 20} 对话完成 {'=' * 20}")
        break

print(client.history())