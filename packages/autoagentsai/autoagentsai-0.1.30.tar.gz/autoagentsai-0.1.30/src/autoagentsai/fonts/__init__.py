import os

# 获取当前目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义字体文件路径
SourceHanSansSC_Regular = os.path.join(current_dir, 'SourceHanSansSC-Regular.otf')

# 导出变量
__all__ = ['SourceHanSansSC_Regular'] 