import os
import csv
import pandas as pd
from openpyxl import load_workbook
from typing import Optional, Dict, List, Union

def excel_to_csv_and_images(input_file, output_csv, img_dir):
    """
    将Excel转换为CSV，并提取其中的所有图片到指定文件夹
    Args:
        input_file (str): Excel文件路径
        output_csv (str): 输出CSV路径
        img_dir (str): 输出图片文件夹路径
    """
    # 1. 读取Excel数据 → CSV
    df = pd.read_excel(input_file)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ CSV 已保存：{output_csv}")

    # 2. 提取图片
    os.makedirs(img_dir, exist_ok=True)
    wb = load_workbook(input_file, data_only=True)
    ws = wb.active

    img_count = 0
    for img in ws._images:  # openpyxl 存储图片在 ws._images
        img_count += 1
        img_name = f"img_{img_count}.png"  # 统一保存为png
        img_path = os.path.join(img_dir, img_name)
        with open(img_path, "wb") as f:
            f.write(img._data())  # 直接写入图像二进制数据
    print(f"✅ 已提取 {img_count} 张图片到：{img_dir}")


def convert_csv_to_json_list(csv_file_path: str):
    """
    读取CSV文件并转换为json列表
    """
    try:
        if not os.path.exists(csv_file_path):
            print(f"CSV文件不存在: {csv_file_path}")
            return []
        
        data = []
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # 转换数值类型
                converted_row = {}
                for key, value in row.items():
                    # 尝试转换为数字
                    try:
                        if '.' in value:
                            converted_row[key] = float(value)
                        else:
                            converted_row[key] = int(value)
                    except (ValueError, AttributeError):
                        # 保持为字符串
                        converted_row[key] = value
                data.append(converted_row)
        
        print(f"成功读取CSV文件: {csv_file_path}, {len(data)} 条记录")
        return data
    except Exception as e:
        print(f"读取CSV文件失败: {csv_file_path}, 错误: {e}")
        return []


def convert_json_to_json_list(data: Optional[Union[Dict, List]]) -> Optional[List[Dict]]:
    """
    转换简化格式为展开的列表格式
    
    Args:
        data: 可以是 None 或 dict
            - None: 返回 None
            - dict: 简化格式 {"key1": "value1", "key2": "value2"} 
              转换为 [{"key": "key1", "value": "value1"}, {"key": "key2", "value": "value2"}]
            
    Returns:
        None 或 list 格式的数据
    """
    if data is None:
        return None
    
    if isinstance(data, dict):
        # 字典格式：直接包含键值对
        # {"key1": "value1", "key2": "value2"} 转换为 [{"key": "key1", "value": "value1"}, {"key": "key2", "value": "value2"}]
        converted = []
        for key, value in data.items():
            converted.append({"key": key, "value": value})
        return converted
    
    # 其他类型不支持
    raise ValueError(f"Unsupported input format: {type(data)}. Expected dict or None.")