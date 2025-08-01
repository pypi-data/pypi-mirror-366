# AutoAgents AI Python SDK

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-0.1.22-green.svg)](https://pypi.org/project/autoagentsai/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

专业的 AutoAgents AI 平台 Python SDK，提供简洁易用的 API 接口，支持智能对话、文件处理、知识库管理等功能。

## ✨ 主要特性

- **🤖 智能对话**：流式对话，支持多轮交互和推理过程展示
- **📁 文件处理**：自动处理多种文件格式（PDF、Word、图片等）
- **🗂️ 知识库管理**：完整的知识库 CRUD 操作和内容搜索
- **🎨 预构建智能体**：PPT 生成、React Agent 等开箱即用的功能
- **🌐 多模态支持**：文本、图片、文件的统一处理接口
- **⚡ 异步支持**：高性能的异步 API 调用

## 🚀 快速开始

### 安装

```bash
pip install autoagentsai
```

或从源码安装：

```bash
git clone https://github.com/your-repo/autoagents-python-sdk.git
cd autoagents-python-sdk
pip install -e .
```

### 基础用法

#### 智能对话

```python
from autoagentsai.client import ChatClient

# 初始化客户端
client = ChatClient(
    agent_id="your_agent_id",
    personal_auth_key="your_auth_key", 
    personal_auth_secret="your_auth_secret"
)

# 发起对话
for event in client.invoke("你好，请介绍一下人工智能"):
    if event['type'] == 'token':
        print(event['content'], end='', flush=True)
    elif event['type'] == 'finish':
        break
```

#### 文件分析

```python
# 上传并分析文件
for event in client.invoke(
    prompt="请分析这个文档的主要内容",
    files=["document.pdf"]
):
    if event['type'] == 'token':
        print(event['content'], end='', flush=True)
```

#### 知识库管理

```python
from autoagentsai.client import KbClient

# 初始化知识库客户端
kb_client = KbClient(
    personal_auth_key="your_auth_key",
    personal_auth_secret="your_auth_secret"
)

# 创建知识库
result = kb_client.create_kb(
    name="技术文档库",
    description="存储技术相关文档"
)

# 查询知识库列表
kb_list = kb_client.query_kb_list()
```

#### PPT 生成

```python
from autoagentsai.prebuilt import create_ppt_agent

# 创建 PPT 智能体
ppt_agent = create_ppt_agent()

# 填充 PPT 模板
ppt_agent.fill(
    prompt="关于人工智能发展的PPT",
    template_file_path="template.pptx",
    output_file_path="output.pptx"
)
```

## 📚 API 参考

### ChatClient

主要的对话客户端，支持流式对话和多模态输入。

#### 方法

- `invoke(prompt, images=None, files=None)` - 发起对话
- `history()` - 获取对话历史

#### 事件类型

- `start_bubble` - 新的回复气泡开始
- `token` - 文本片段（用于打字机效果）
- `reasoning_token` - AI 推理过程
- `end_bubble` - 回复气泡结束
- `finish` - 对话完成

### KbClient

知识库管理客户端。

#### 方法

- `create_kb(name, description)` - 创建知识库
- `query_kb_list()` - 查询知识库列表
- `get_kb_detail(kb_id)` - 获取知识库详情
- `delete_kb(kb_id)` - 删除知识库

## 🛠️ 环境要求

- Python 3.11+
- 依赖包：
  - `pydantic>=2.11.7`
  - `requests>=2.32.4`

## 🔧 配置

### 环境设置

```python
# 测试环境（默认）
base_url = "https://uat.agentspro.cn"

# 生产环境
base_url = "https://agentspro.cn"
```

### 获取 API 密钥

1. 登录 AutoAgents AI 平台
2. 右上角 - 个人密钥
3. 复制 `personal_auth_key` 和 `personal_auth_secret`

### 获取 Agent ID

1. 进入 Agent 详情页
2. 点击"分享" - "API"
3. 复制 Agent ID

## 📖 更多示例

查看 `playground/` 目录获取更多使用示例：

- `playground/chat/` - 对话功能示例
- `playground/ppt/` - PPT 生成示例  
- `playground/kb/` - 知识库管理示例
- `playground/react_agent/` - React Agent 示例

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

- 📧 邮箱：forhheart5532@gmail.com
- 📚 文档：[AutoAgents AI 官方文档](https://docs.agentspro.cn)
- 🐛 问题报告：[GitHub Issues](https://github.com/your-repo/autoagents-python-sdk/issues)
