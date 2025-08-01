


# 模块使用指南

## 基础用法

### 创建FlowGraph实例
```python
from src.autoagentsai.graph.FlowGraph import FlowGraph

# 创建FlowGraph实例（必需认证参数）
graph = FlowGraph(
    personal_auth_key="your_auth_key",
    personal_auth_secret="your_auth_secret", 
    base_url="https://uat.agentspro.cn"  # 可选，有默认值
)
```

### 添加节点的基本语法
```python
graph.add_node(
    node_id="节点唯一标识",           # 必需：节点ID，在整个流程中唯一
    module_type="模块类型",          # 必需：模块类型，见下面详细说明
    position={"x": 100, "y": 100},   # 必需：节点在画布上的位置
    inputs={                         # 可选：输入参数配置
        "参数名": "参数值"
    }
)
```

### 添加连接边
```python
graph.add_edge(
    source="源节点ID",
    target="目标节点ID", 
    source_handle="源输出端口",     # 可选，默认""
    target_handle="目标输入端口"    # 可选，默认""
)
```

### 编译和部署
```python
graph.compile(
    name="智能体名称",              # 可选，默认"未命名智能体"
    avatar="头像URL",              # 可选，有默认头像
    intro="智能体介绍",            # 可选
    category="分类",               # 可选
    prologue="开场白"              # 可选
)
```

---

## 模块详细说明

## 1. 用户提问（questionInput）

### 📌 模块功能说明
用于主动向用户请求输入信息。支持的输入类型包括文本、文档和图片（不可同时选择图片和文档）。该模块通常为流程的起点，也可在任意节点后用于再次获取用户输入。模块本身不执行任何智能处理，仅负责采集用户数据，并将其传递给下游模块使用。

### 📝 SDK使用方法

```python
graph.add_node(
    node_id="user_input",
    module_type="questionInput",
    position={"x": 100, "y": 100},
    inputs={
        # 基础开关配置
        "inputText": True,          # 是否启用文本输入（默认True）
        "uploadFile": False,        # 是否启用文档上传（默认False）
        "uploadPicture": False,     # 是否启用图片上传（默认False）
        
        # 高级功能开关
        "fileUpload": False,        # 是否启用文档审查功能（默认False）
        "fileContrast": False,      # 是否启用文档比对功能（默认False）
        "fileInfo": [],             # 文档分组信息（仅文档比对时使用）
        "initialInput": True        # 是否作为初始输入（默认True）
    }
)
```
### 🔶 参数详细说明

| 参数名 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `inputText` | boolean | `True` | 是否启用文本输入功能 |
| `uploadFile` | boolean | `False` | 是否启用文档上传功能 |
| `uploadPicture` | boolean | `False` | 是否启用图片上传功能 |
| `fileUpload` | boolean | `False` | 是否启用文档审查功能 |
| `fileContrast` | boolean | `False` | 是否启用文档比对功能 |
| `fileInfo` | list | `[]` | 文档分组信息（仅文档比对时使用） |
| `initialInput` | boolean | `True` | 是否作为初始流程输入 |

### 🔷 输出变量（可在后续模块中引用）

| 变量名 | 类型 | 说明 |
|-------|------|------|
| `{{userChatInput}}` | string | 用户文本输入内容 |
| `{{files}}` | file | 用户上传的文档列表 |
| `{{images}}` | image | 用户上传的图片列表 |
| `{{unclickedButton}}` | boolean | 用户是否未点击按钮 |
| `{{finish}}` | boolean | 模块运行完成标志 |

### ✅ 使用规则与限制

- **互斥限制**：`uploadFile` 和 `uploadPicture` 不能同时为 `True`
- **文档功能**：如需文档审查或比对，需同时开启 `fileUpload` 或 `fileContrast`
- **连接要求**：通常作为流程起点，需要连接 `{{finish}}` 到下游模块
- **数据传递**：根据业务需求连接相应输出变量到下游模块

### 🧠 常用配置示例

```python
# 示例1：纯文本输入
graph.add_node(
    node_id="text_input",
    module_type="questionInput", 
    position={"x": 100, "y": 100},
    inputs={
        "inputText": True,
        "uploadFile": False,
        "uploadPicture": False
    }
)

# 示例2：文档上传 + 文本输入
graph.add_node(
    node_id="doc_input",
    module_type="questionInput",
    position={"x": 100, "y": 100}, 
    inputs={
        "inputText": True,
        "uploadFile": True,      # 开启文档上传
        "uploadPicture": False,  # 必须关闭图片上传
        "fileUpload": True       # 开启文档审查
    }
)

# 示例3：图片上传 + 文本输入
graph.add_node(
    node_id="image_input",
    module_type="questionInput",
    position={"x": 100, "y": 100},
    inputs={
        "inputText": True,
        "uploadFile": False,     # 必须关闭文档上传
        "uploadPicture": True    # 开启图片上传
    }
)
```

---

## 2. 智能对话（aiChat）

### 📌 模块功能说明
该模块通过接入大语言模型（LLM），实现智能问答、内容生成、信息加工等功能。它接受用户文本输入、图片信息、知识库内容等多种信息来源，并根据配置的提示词（Prompt）与参数设置返回 AI 生成的内容，常用于回复用户问题或加工上下文信息。

### 📝 SDK使用方法

```python
graph.add_node(
    node_id="ai_chat",
    module_type="aiChat",
    position={"x": 300, "y": 100},
    inputs={
        # 模型基础配置
        "model": "glm-4-airx",                 # 选择LLM模型（必填）
        "quotePrompt": "你是一个智能助手...",     # 提示词（可选）
        
        # 输入数据配置（通过变量引用）
        "text": "{{userChatInput}}",           # 文本输入（通常连接用户输入）
        "images": "{{images}}",                # 图片输入（可选）
        "knSearch": "{{quoteQA}}",             # 知识库搜索结果（可选）
        
        # 模型参数配置
        "temperature": 0.1,                    # 创意性控制 (0-1)
        "maxToken": 3000,                      # 回复字数上限
        "stream": True,                        # 是否对用户可见
        "historyText": 3,                      # 上下文轮数 (0-6)
        
        # 高级配置
        "knConfig": "使用检索到的内容回答问题"     # 知识库高级配置（可选）
    }
)
```

### 🔷 输出变量（可在后续模块中引用）

| 变量名 | 类型 | 说明 |
|-------|------|------|
| `{{answerText}}` | string | AI生成的回复内容 |
| `{{isResponseAnswerText}}` | boolean | 模型处理完成标志 |
| `{{finish}}` | boolean | 模块运行完成标志 |

✅ 使用规则与限制
输入项连接要求
激活输入必须至少连接一个：
switch：上游所有模块完成时触发
switchAny：任一上游完成即可触发（推荐使用）
text 通常 必须连接，用于接收来自用户的文本输入（如 questionInput.userChatInput）。未连接则模型缺少主要输入内容。
其他可选输入项请根据业务场景决定是否连接和配置：
images：如需处理用户上传图片，则连接 questionInput.images
knSearch：如需融合知识库信息，则连接知识库搜索结果
knConfig：如有知识库高级配置需求，可设置控制模型行为（如片段筛选、结构化注入等）
historyText：设置模型可访问的历史对话轮数（0~6），提升多轮上下文理解能力
model：必须配置，决定使用哪种 LLM，支持不同模型策略选择
quotePrompt：可配置为模型固定输入前缀，引导语气、身份、限制范围等
stream：若开启，表示回复内容将展示给用户（对话类场景应开启）
temperature、maxToken：可调节创意性与回复长度，默认保守设置即可
输出项连接建议
必须连接 finish 输出 至下游模块的 switchAny，用于触发后续流程执行
answerText 输出为模型生成的回复内容：
如需展示给用户（如 UI 渲染），可连接展示模块或输出端
如仅为中间处理结果，可按需传递到后续逻辑模块
isResponseAnswerText 表示处理结束的另一标志信号，可选连接，便于更精细的控制

🧠 SOP设计建议
典型用法： 在用户输入后接入此模块，用于处理用户请求，生成自然语言回复内容
上游触发： 通常由 questionInput 模块的 finish 激活，同时连接用户输入作为 text 输入
回复生成：
默认建议开启 stream，直接将模型回复显示给用户
若为中间处理用途（如文本分析、摘要抽取等），可关闭 stream，并按需传递 answerText 到下一模块
知识融合： 若业务涉及知识库检索或嵌入文档内容，可连接 knSearch 和配置 knConfig 参数
分段处理： 多轮多步骤处理可串联多个 aiChat 模块，适当设置 historyText 形成递进式处理链路
模块复用： 建议通过 Prompt 和模型切换适配不同角色与任务，如总结、生成邮件、格式化回复等
激活策略： 推荐统一使用 switchAny 激活以增强容错性，确保模块能被正常触发执行

## 3. HTTP调用（httpInvoke）

### 📌 模块功能说明
该模块用于向外部服务发起 HTTP 请求（如 GET / POST / PUT 等），并将返回结果作为流程的一部分进行处理。适用于调用外部数据库、搜索服务、分析服务等一切需要远程请求的场景。

### 📝 SDK使用方法

```python
graph.add_node(
    node_id="http_call",
    module_type="httpInvoke",
    position={"x": 400, "y": 100},
    inputs={
        # 请求配置
        "url": """post https://api.example.com/search
data-type json
token your_api_token
Content-Type application/json""",  # 请求地址和配置
        
        # 请求体（通过变量引用）
        "_requestBody_": "{{requestData}}"  # 完整的POST请求体JSON数据
    }
)
```
### 🔶 参数详细说明

| 参数名 | 类型 | 默认值 | 必填 | 说明 |
|-------|------|-------|------|------|
| `url` | string | `""` | ✅ | 请求配置（包含方法、地址、headers） |
| `_requestBody_` | string | `""` | ❌ | POST请求体的JSON数据（变量引用） |

### 🔷 输出变量（可在后续模块中引用）

| 变量名 | 类型 | 说明 |
|-------|------|------|
| `{{_success_}}` | boolean | 请求成功标志 |
| `{{_failed_}}` | boolean | 请求失败标志 |
| `{{_response_}}` | string | 接口返回的原始JSON字符串 |
| `{{finish}}` | boolean | 模块运行完成标志 |

### ✅ 使用规则与限制

- **URL配置格式**：必须按以下格式配置
  ```
  方法 地址
  data-type json
  token 认证令牌
  header名 header值
  ```
- **支持的HTTP方法**：`get`, `post`, `put`, `patch`, `delete`
- **数据类型**：推荐使用 `json`，也支持 `form`, `query`
- **请求体**：POST/PUT请求需要通过 `_requestBody_` 传入JSON数据
- **限制**：暂不支持 form-data、文件上传等复杂格式

### 🧠 常用配置示例

```python
# 示例1：GET请求
graph.add_node(
    node_id="get_data",
    module_type="httpInvoke",
    position={"x": 300, "y": 100},
    inputs={
        "url": """get https://api.example.com/users
token Bearer abc123
Accept application/json"""
    }
)

# 示例2：POST请求
graph.add_node(
    node_id="post_data", 
    module_type="httpInvoke",
    position={"x": 500, "y": 100},
    inputs={
        "url": """post https://api.example.com/users
data-type json
Authorization Bearer {{token}}
Content-Type application/json""",
        "_requestBody_": "{{userInfo}}"  # 来自上游模块的JSON数据
    }
)
```
🧠 SOP设计建议
用途定位：适用于调用外部服务、数据库、搜索引擎、内容分析接口等
举例：用户提问 → 提取关键词 → HTTP接口搜索商品/法规 → 返回结果交给大模型处理或展示
典型流程位置：
在 questionInput / aiChat 输出后插入此模块，作为“数据抓取中枢”使用
接收结构化输入 → 发起远程请求 → 输出结果交下游处理或展示
分支处理：
推荐将 _success_ / _failed_ 分别连接不同后续模块，实现流程健壮性控制
如成功后进入 aiChat 总结
失败后可通过额外模块提示用户“接口调用失败”
可扩展性建议：
将 url 与 requestBody 做参数化抽象，可以提高复用性（如生成不同类型接口调用模板）
若后续支持动态 token / header，可通过变量拼接方式注入（在 prompt 或前置模块中预处理）
结合使用建议：
通常与以下模块联用：
questionInput 提供参数或关键词
aiChat 生成结构化请求体
aiChat / 展示模块处理返回结果并呈现

## 4. 确定回复（confirmreply）
### 📌 模块功能说明
该模块用于在满足特定触发条件时，输出一段预设的文本内容或接收并转发来自上游模块的文本结果。常用于提示确认、信息回显、引导性回复等流程场景中。支持静态配置内容或动态内容输入，适配多种用户交互场景。

### 📝 SDK使用方法

```python
graph.add_node(
    node_id="confirm_reply",
    module_type="confirmreply",
    position={"x": 600, "y": 100},
    inputs={
        # 回复内容配置
        "text": "操作已完成！您的请求已成功处理。",  # 静态文本
        # "text": "{{processResult}}",  # 或使用变量引用动态内容
        
        # 可见性控制
        "stream": True  # 是否对用户可见（默认True）
    }
)
```

### 🔶 参数详细说明

| 参数名 | 类型 | 默认值 | 必填 | 说明 |
|-------|------|-------|------|------|
| `text` | string | `"默认提示文本"` | ❌ | 回复内容（支持变量引用） |
| `stream` | boolean | `True` | ❌ | 是否对用户可见 |

### 🔷 输出变量（可在后续模块中引用）

| 变量名 | 类型 | 说明 |
|-------|------|------|
| `{{text}}` | string | 模块输出的回复内容 |
| `{{finish}}` | boolean | 模块运行完成标志 |

### ✅ 使用规则与特点

- **内容灵活**：支持静态文本或变量引用动态内容
- **格式支持**：支持 `\n` 换行符和变量占位符
- **可见性控制**：通过 `stream` 控制是否对用户可见
- **变量覆盖**：外部输入会覆盖静态配置的内容

### 🧠 常用配置示例

```python
# 示例1：静态确认回复
graph.add_node(
    node_id="success_confirm",
    module_type="confirmreply",
    position={"x": 700, "y": 100},
    inputs={
        "text": "✅ 操作成功完成！\n您的请求已处理。",
        "stream": True
    }
)

# 示例2：动态内容回复
graph.add_node(
    node_id="dynamic_reply",
    module_type="confirmreply", 
    position={"x": 800, "y": 200},
    inputs={
        "text": "处理结果：{{processResult}}\n状态：{{status}}",
        "stream": True
    }
)

# 示例3：内部流转（不显示给用户）
graph.add_node(
    node_id="internal_log",
    module_type="confirmreply",
    position={"x": 900, "y": 300},
    inputs={
        "text": "内部日志：{{logMessage}}",
        "stream": False  # 仅内部使用，不显示给用户
    }
)
```

---

## 5. 知识库搜索（knowledgesSearch）
### 📌 模块功能说明
该模块用于在关联的知识库中进行搜索，根据用户输入的信息智能匹配相关内容，辅助智能对话模块提供更精准的回答。支持相似度阈值设置、重排序模型优化和召回数限制等参数，提升知识检索的准确性和相关性。

### 📝 SDK使用方法

```python
graph.add_node(
    node_id="knowledge_search",
    module_type="knowledgesSearch",
    position={"x": 300, "y": 200},
    inputs={
        # 基础配置
        "text": "{{userChatInput}}",         # 搜索文本（变量引用）
        "datasets": ["kb_001", "kb_002"], # 关联的知识库ID列表
        
        # 检索参数优化
        "similarity": 0.2,               # 相似度阈值 (0-1)
        "vectorSimilarWeight": 1.0,      # 向量相似度权重 (0-1)
        "topK": 20,                      # 召回数量 (0-100)
        
        # 重排序配置（可选）
        "enableRerank": False,           # 是否开启重排序
        "rerankModelType": "oneapi-xinference:bce-rerank",  # 重排序模型
        "rerankTopK": 10                 # 重排序召回数 (0-20)
    }
)
```

### 🔶 参数详细说明

| 参数名 | 类型 | 默认值 | 必填 | 范围 | 说明 |
|-------|------|-------|------|------|------|
| `text` | string | `""` | ✅ | - | 搜索输入文本（支持变量引用） |
| `datasets` | array | `[]` | ✅ | - | 关联的知识库ID列表 |
| `similarity` | number | `0.2` | ❌ | 0-1 | 相似度阈值，低于此值的结果将被过滤 |
| `vectorSimilarWeight` | number | `1.0` | ❌ | 0-1 | 向量相似度权重（1-此值为关键词权重） |
| `topK` | number | `20` | ❌ | 0-100 | 召回的相关切片数量 |
| `enableRerank` | boolean | `False` | ❌ | - | 是否启用重排序模型（消耗更多资源） |
| `rerankModelType` | string | `"oneapi-xinference:bce-rerank"` | ❌ | - | 重排序模型类型 |
| `rerankTopK` | number | `10` | ❌ | 0-20 | 重排序后的召回数量 |

### 🔷 输出变量（可在后续模块中引用）

| 变量名 | 类型 | 说明 |
|-------|------|------|
| `{{isEmpty}}` | boolean | 未搜索到相关知识时为true |
| `{{unEmpty}}` | boolean | 搜索到相关知识时为true |  
| `{{quoteQA}}` | search | 知识库搜索结果数组 |
| `{{finish}}` | boolean | 模块运行完成标志 |

### ✅ 使用规则与特点

- **知识库必填**：必须指定 `datasets` 关联的知识库
- **分支控制**：通过 `isEmpty`/`unEmpty` 实现搜索结果分支处理
- **参数调优**：相似度阈值和召回数可根据业务需求调整
- **重排序权衡**：重排序提升精度但消耗更多资源，需谨慎开启

### 🧠 常用配置示例

```python
# 示例1：基础知识库搜索
graph.add_node(
    node_id="kb_search", 
    module_type="knowledgesSearch",
    position={"x": 400, "y": 200},
    inputs={
        "text": "{{userChatInput}}",
        "datasets": ["customer_service_kb"]
    }
)

# 示例2：高精度搜索（开启重排序）
graph.add_node(
    node_id="precise_search",
    module_type="knowledgesSearch",
    position={"x": 500, "y": 300},
    inputs={
        "text": "{{questionText}}",
        "datasets": ["legal_kb", "policy_kb"],
        "similarity": 0.3,
        "topK": 15,
        "enableRerank": True,
        "rerankTopK": 5
    }
)

# 示例3：混合检索（关键词+向量）
graph.add_node(
    node_id="hybrid_search",
    module_type="knowledgesSearch", 
    position={"x": 600, "y": 400},
    inputs={
        "text": "{{searchQuery}}",
        "datasets": ["product_kb"],
        "vectorSimilarWeight": 0.7,  # 70%向量 + 30%关键词
        "similarity": 0.25,
        "topK": 30
    }
)
```

---

## 6. 通用文档解析（pdf2md）
### 📌 模块功能说明
该模块用于将各种通用文档格式（如 PDF、Word 等）解析并转换成 Markdown 格式文本，方便后续文本处理、展示和智能分析。

### 📝 SDK使用方法

```python
graph.add_node(
    node_id="doc_parser",
    module_type="pdf2md",
    position={"x": 400, "y": 300},
    inputs={
        # 文档输入
        "files": "{{uploadedFiles}}",    # 待解析的文档文件（变量引用）
        
        # 模型选择
        "pdf2mdType": "general"          # 解析模型类型
    }
)
```

### 🔶 参数详细说明

| 参数名 | 类型 | 默认值 | 必填 | 说明 |
|-------|------|-------|------|------|
| `files` | file | - | ✅ | 待解析的文档文件（支持变量引用） |
| `pdf2mdType` | string | `"general"` | ✅ | 解析模型类型，影响转换效果和识别精度 |

### 🔷 输出变量（可在后续模块中引用）

| 变量名 | 类型 | 说明 |
|-------|------|------|
| `{{pdf2mdResult}}` | string | 转换后的Markdown格式文本 |
| `{{success}}` | boolean | 文档解析成功标志 |
| `{{failed}}` | boolean | 文档解析失败标志 |
| `{{finish}}` | boolean | 模块运行完成标志 |

### ✅ 使用规则与特点

- **支持格式**：PDF、Word、Excel等多种文档格式
- **模型选择**：根据文档类型选择合适的解析模型
- **分支控制**：通过 `success`/`failed` 实现解析结果分支处理
- **输出格式**：统一输出Markdown格式，便于后续处理

### 🧠 常用配置示例

```python
# 示例1：基础文档解析
graph.add_node(
    node_id="parse_doc",
    module_type="pdf2md",
    position={"x": 300, "y": 200},
    inputs={
        "files": "{{userUploadedFiles}}",
        "pdf2mdType": "general"
    }
)

# 示例2：解析结果分支处理
# 成功分支
graph.add_node(
    node_id="process_success",
    module_type="aiChat",
    position={"x": 500, "y": 150},
    inputs={
        "text": "请分析以下文档内容：{{pdf2mdResult}}",
        "model": "glm-4-airx"
    }
)

# 失败分支  
graph.add_node(
    node_id="handle_failure",
    module_type="confirmreply",
    position={"x": 500, "y": 250},
    inputs={
        "text": "文档解析失败，请检查文档格式或重新上传",
        "stream": True
    }
)

# 添加连接边
graph.add_edge("parse_doc", "process_success", "success", "switchAny")
graph.add_edge("parse_doc", "handle_failure", "failed", "switchAny")
```

## 7. 添加记忆变量（addMemoryVariable）

### 📌 模块功能说明
该模块用于将某个变量值存储为智能体的记忆变量，供后续流程中其他模块通过 `{{变量名}}` 的形式引用，实现跨模块共享信息、上下文记忆、动态引用等功能。
适用于场景如：记录用户反馈、抽取结果中间变量、保存文件/图片等结果，用于后续模型处理或响应生成。

### 📝 SDK使用方法

```python
# 基础用法：单个记忆变量
memory_variable_inputs = {}
memory_variable_inputs["question"] = "{{answerText}}"

[
    {
        "key": "question",
        "value": "{{answerText}}",
        "value_type": "text"
    },
    {
        "key": "feedback",
        "value": "{{aireply}}",
        "value_type": "text"
    }
]


graph.add_node(
    node_id="addMemoryVariable1",
    module_type="addMemoryVariable",
    position={"x": 1500, "y": 300},
    inputs=memory_variable_inputs
)

# 高级用法：多个记忆变量
graph.add_node(
    node_id="save_multiple",
    module_type="addMemoryVariable", 
    position={"x": 500, "y": 200},
    inputs={
        "user_question": "{{userChatInput}}",
        "ai_answer": "{{answerText}}",
        "uploaded_file": "{{files}}",
        "user_image": "{{images}}",
        "search_result": "{{quoteQA}}"
    }
)
```

### 🔶 支持的ValueType类型

`addMemoryVariable` 模块支持以下固定的数据类型：

| ValueType | 说明 | 适用场景 |
|-----------|------|----------|
| `string` | 文本字符串 | 用户输入内容、AI回答、识别摘要等 |
| `boolean` | 布尔值 | 是否成功、是否选择某项、开关状态等 |
| `file` | 文档信息 | 上传的PDF、DOC、Excel等文件 |
| `image` | 图片信息 | 上传的图片资源 |
| `search` | 知识库搜索结果 | 知识库检索返回的内容 |
| `any` | 任意类型 | 动态结构或未知类型数据 |
### 📊 使用示例

```python
# 不同类型的记忆变量示例
inputs = {
    "question": "{{answerText}}",        # string类型（文本）
    "user_file": "{{uploadedFile}}",     # file类型（文件）
    "user_image": "{{userPhoto}}",       # image类型（图片）
    "is_success": "{{result}}",          # boolean类型（布尔值）
    "kb_result": "{{searchResult}}",     # search类型（知识库搜索）
    "config_data": "{{configuration}}"   # any类型（任意类型）
}
```

### 🔷 输出变量（可在后续模块中引用）

**无直接输出**，但会在智能体全局注册记忆变量：
- 变量名即为 `inputs` 中的key
- 后续模块可通过 `{{变量名}}` 引用
- valueType会根据实际数据内容自动确定类型


### 常用配置示例

```python
# 示例1：保存AI回答供后续引用
memory_variable_inputs = []
input_1 = {
    "key": "",
    "value_type": ""
}

# 若需要多变量，以此类推
# input_2 = {
#    "key": "",
#    "value_type": ""
# }

memory_variable_inputs.append(input_1)
# memory_variable_inputs.append(input_2) 

graph.add_node(
    node_id="addMemoryVariable1",
    module_type="addMemoryVariable",
    position={"x": 1500, "y": 300},
    inputs=memory_variable_inputs
)

```

---

## 完整工作流示例

```python
from src.autoagentsai.graph.FlowGraph import FlowGraph

# 创建FlowGraph实例
graph = FlowGraph(
    personal_auth_key="your_auth_key",
    personal_auth_secret="your_auth_secret"
)

# 1. 用户输入
graph.add_node(
    node_id="user_input",
    module_type="questionInput",
    position={"x": 100, "y": 100},
    inputs={
        "inputText": True,
        "uploadFile": False
    }
)

# 2. AI处理
graph.add_node(
    node_id="ai_chat",
    module_type="aiChat",
    position={"x": 300, "y": 100},
    inputs={
        "model": "glm-4-airx",
        "text": "{{userChatInput}}",
        "temperature": 0.1,
        "stream": True
    }
)

# 3. 保存记忆变量
graph.add_node(
    node_id="save_memory",
    module_type="addMemoryVariable",
    position={"x": 500, "y": 100},
    inputs={
        "question": "{{userChatInput}}",  # string类型（文本）
        "ai_answer": "{{answerText}}"     # string类型（文本）
    }
)

# 4. 确认回复
graph.add_node(
    node_id="confirm_reply",
    module_type="confirmreply",
    position={"x": 700, "y": 100},
    inputs={
        "text": "已保存问题：{{question}} 和回答：{{ai_answer}}",
        "stream": True
    }
)

# 添加连接边
graph.add_edge("user_input", "ai_chat", "finish", "switchAny")
graph.add_edge("ai_chat", "save_memory", "finish", "switchAny")
graph.add_edge("save_memory", "confirm_reply", "finish", "switchAny")

# 编译和部署
graph.compile(
    name="智能问答助手",
    intro="具有记忆功能的智能问答助手",
    category="对话工具"
)
```
