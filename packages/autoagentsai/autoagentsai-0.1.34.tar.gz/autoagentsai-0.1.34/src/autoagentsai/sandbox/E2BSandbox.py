from typing import Dict, Any
import base64
from ..client import ChatClient
from ..utils.extractor import extract_python_code
from e2b_code_interpreter import Sandbox


class E2BSandboxService:
    """E2B Sandbox服务，用于安全执行Python代码"""
    def __init__(self, api_key: str):
        self.sandbox = Sandbox(timeout=3000, api_key=api_key)

    def run_code(self, code: str):
        """执行Python代码并返回结果
        
        Args:
            code: 要执行的Python代码
            
        Returns:
            Dict包含执行结果，包括success、output、error、images、generated_code等
        """

        execution = self.sandbox.run_code(code)
        result_idx = 0 
        for result in execution.results: 
            if result.png: 
                # Save the png to a file
                # The png is in base64 format.
                with open(f'chart-{result_idx}.png', 'wb') as f: 
                    f.write(base64.b64decode(result.png)) 
                print(f'Chart saved to chart-{result_idx}.png') 
                result_idx += 1 
        return execution

    def analyze_csv(self, user_query: str, file_path: str) -> Dict[str, Any]:
        """使用AI生成代码并分析CSV数据"""
        
        # 读取本地CSV文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # 上传CSV文件到沙箱
        filename = file_path.split('/')[-1]  # 提取文件名
        dataset_path = self.sandbox.files.write(filename, file_content).path
        
        # 构建分析提示词
        prompt = f"""
我有一个CSV文件，路径是 {dataset_path}。

用户的分析需求：{user_query}

请你：
1. **首先必须读取CSV文件并检查实际的列名和数据类型**
2. **只使用实际存在的列进行分析，不要假设任何列名**
3. 根据实际的数据类型（数值型、类别型）选择合适的分析方法
4. 生成相应的可视化图表
5. 输出基于实际数据的关键发现

**严格要求**：
- 先用 df.columns 查看实际列名
- 用 df.dtypes 查看数据类型
- 根据实际的列名和数据进行分析
- 不要硬编码任何列名（如 'income', 'gender' 等）
- 每个图表都必须保存为PNG文件

请直接编写Python代码：

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体和图表样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# 读取CSV文件
df = pd.read_csv('{dataset_path}')

# 1. 必须首先检查数据结构
print("=== 数据基本信息 ===")
print("列名:", df.columns.tolist())
print("数据形状:", df.shape)
print("\\n数据类型:")
print(df.dtypes)
print("\\n前5行数据:")
print(df.head())
print("\\n描述性统计:")
print(df.describe(include='all'))

# 2. 根据实际列名识别数值型和类别型变量
numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

# 3. 数值型变量分析（只分析实际存在的数值列）
chart_count = 0
if numeric_columns:
    for col in numeric_columns:
        chart_count += 1
        plt.figure()
        sns.histplot(df[col], kde=True)
        plt.title(f'分布')
        plt.xlabel(col)
        plt.ylabel('频数')
        plt.savefig(f'chart_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

```

只返回上面的Python代码，不要添加任何其他内容。"""
        
        # 使用模型客户端生成代码
        try:
            chat_client = ChatClient(
                agent_id="7e46d18945fc49379063e3057a143c58",
                personal_auth_key="339859fa69934ea8b2b0ebd19d94d7f1",
                personal_auth_secret="93TsBecJplOawEipqAdF7TJ0g4IoBMtA",
                base_url="https://uat.agentspro.cn"
            )

            content = ""
            for event in chat_client.invoke(prompt):
                if event['type'] == 'token':
                    content += event['content']
                elif event['type'] == 'finish':
                    break
            content = extract_python_code(content)

            print(f"AI generated code:\n{content}")

            try:
                # 执行代码
                execution_result = self.run_code(content)

                print(f"Execution result:\n{execution_result}")
                return execution_result
            except Exception as e:
                print(f"Error executing code: {e}")
                return {"error": str(e)}
        except Exception as e:
            print(f"Error generating code: {e}")
            return {"error": str(e)}