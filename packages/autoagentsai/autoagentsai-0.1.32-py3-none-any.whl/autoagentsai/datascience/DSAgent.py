from ..client import ChatClient
from ..utils.extractor import extract_python_code
from ..sandbox import LocalSandboxService
import pandas as pd

class DSAgent:
    def __init__(self):
        self.sandbox = LocalSandboxService()

    def get_csv_info(self, file_path: str):
        """获取CSV文件的列名、数据类型、数据形状、前5行数据、描述性统计"""
        df = pd.read_csv(file_path)
        return df.columns.tolist(), df.dtypes, df.shape, df.head(), df.describe(include='all')

    def analyze_csv(self, user_query: str, file_path: str, verbose: bool = False):
        """使用AI生成代码并分析CSV数据"""
        columns, dtypes, shape, head, describe = self.get_csv_info(file_path)

        dataset_path = file_path
        # 构建优化的分析提示词
        prompt = f"""
你是一位专业的数据科学家，需要编写完整的Python代码来分析CSV数据。

**任务**：分析CSV文件并生成可视化图表
- 文件路径：{dataset_path}
- 用户需求：{user_query}

**预览信息**（仅供参考，请以实际读取的数据为准）：
- 数据形状：{shape}
- 列名：{columns}
- 数据类型：{dtypes}

**严格要求**：
1. 必须从实际读取CSV开始，不要依赖预览信息
2. 只使用文件中实际存在的列名，不要硬编码任何列名
3. 根据实际数据类型选择合适的分析方法
4. 所有图表必须保存为PNG文件，文件名要有意义
5. 设置中文字体支持，确保图表标题和标签正确显示
6. 每个图表都要关闭（plt.close()）以释放内存

**代码模板**：
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
from autoagentsai.fonts import SourceHanSansSC_Regular
warnings.filterwarnings('ignore')

# 设置中文字体支持
import matplotlib.font_manager as fm
zhfont1 = fm.FontProperties(fname=SourceHanSansSC_Regular)

sns.set_style("whitegrid")

# 读取CSV文件
df = pd.read_csv('{dataset_path}')

# 1. 数据概览
print("=== 数据基本信息 ===")
print(f"数据形状: {{df.shape}}")
print(f"列名: {{df.columns.tolist()}}")
print(f"数据类型:\\n{{df.dtypes}}")
print(f"\\n前5行数据:\\n{{df.head()}}")
print(f"\\n描述性统计:\\n{{df.describe(include='all')}}")

# 2. 识别数据类型
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

print(f"\\n数值型列: {{numeric_cols}}")
print(f"类别型列: {{categorical_cols}}")

# 3. 数据分析和可视化（根据实际列名）
chart_count = 0

# 数值型变量分析
for col in numeric_cols:
    chart_count += 1
    plt.figure(figsize=(10, 6))
    sns.histplot(df[col], kde=True, bins=20)
    plt.title(f'{{col}}的分布', fontproperties=zhfont1)
    plt.xlabel(col, fontproperties=zhfont1)
    plt.ylabel('频数', fontproperties=zhfont1)
    plt.savefig(f'chart_{{chart_count:02d}}_{{col}}_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

# 类别型变量分析
for col in categorical_cols:
    if df[col].nunique() <= 20:  # 只分析类别不超过20个的变量
        chart_count += 1
        plt.figure(figsize=(10, 6))
        value_counts = df[col].value_counts()
        if len(value_counts) <= 10:
            # 少于10个类别用条形图
            value_counts.plot(kind='bar')
            plt.title(f'{{col}}分布')
            plt.xticks(rotation=45)
        else:
            # 多于10个类别用饼图显示前10个
            top_values = value_counts.head(10)
            plt.pie(top_values.values, labels=top_values.index, autopct='%1.1f%%')
            plt.title(f'{{col}}前10类别分布', fontproperties=zhfont1)
        plt.savefig(f'chart_{{chart_count:02d}}_{{col}}_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

# 相关性分析
if len(numeric_cols) > 1:
    chart_count += 1
    plt.figure(figsize=(10, 8))
    corr_matrix = df[numeric_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, square=True)
    plt.title('数值变量相关性热力图', fontproperties=zhfont1)
    plt.savefig(f'chart_{{chart_count:02d}}_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

# 组合分析（类别 vs 数值）
if categorical_cols and numeric_cols:
    for cat_col in categorical_cols[:2]:  # 最多选择2个类别变量
        if df[cat_col].nunique() <= 10:  # 类别不超过10个
            for num_col in numeric_cols[:2]:  # 最多选择2个数值变量
                chart_count += 1
                plt.figure(figsize=(12, 6))
                sns.boxplot(data=df, x=cat_col, y=num_col, palette="pastel")
                plt.title(f'{{cat_col}}与{{num_col}}的关系', fontproperties=zhfont1)
                plt.xticks(rotation=45, fontproperties=zhfont1)
                plt.savefig(f'chart_{{chart_count:02d}}_{{cat_col}}_vs_{{num_col}}.png', dpi=300, bbox_inches='tight')
                plt.close()

# 4. 关键发现总结
print("\\n=== 关键发现 ===")
for col in numeric_cols:
    print(f"{{col}}: 均值={{df[col].mean():.2f}}, 中位数={{df[col].median():.2f}}, 标准差={{df[col].std():.2f}}")

for col in categorical_cols:
    if df[col].nunique() <= 50:
        mode_value = df[col].mode()[0] if not df[col].mode().empty else 'N/A'
        print(f"{{col}}: 共{{df[col].nunique()}}个类别, 最常见: '{{mode_value}}'")

print(f"\\n✅ 分析完成，共生成 {{chart_count}} 张图表")
```

请只返回上述完整的Python代码，确保所有变量名都使用实际数据中存在的列名。"""
        
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
                    if verbose:
                        print(event['content'], end='', flush=True)
                    
            content = extract_python_code(content)

            print(f"AI generated code:\n{content}")

            try:
                # 执行代码
                execution_result = self.sandbox.run_code(content)

                print(f"Execution result:\n{execution_result}")
                return execution_result
            except Exception as e:
                print(f"Error executing code: {e}")
                return {"error": str(e)}
        except Exception as e:
            print(f"Error generating code: {e}")
            return {"error": str(e)} 