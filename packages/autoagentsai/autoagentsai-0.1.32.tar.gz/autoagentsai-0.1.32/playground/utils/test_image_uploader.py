import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.autoagentsai.utils.uploader import ImageUploader, create_file_like
from io import BytesIO
import json

def create_test_image():
    """创建一个简单的测试图片（1x1像素的PNG）"""
    # 创建一个最小的PNG图片数据
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc\x60\x00\x02\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    return BytesIO(png_data)

def test_image_uploader():
    """测试ImageUploader的各种功能"""
    
    # 从环境变量获取JWT token，如果没有则使用测试token
    jwt_token = os.getenv('AUTOAGENTS_JWT_TOKEN', 'your_test_token_here')
    
    if jwt_token == 'your_test_token_here':
        print("警告: 请设置环境变量 AUTOAGENTS_JWT_TOKEN 或在代码中填入实际的JWT token")
        print("export AUTOAGENTS_JWT_TOKEN='your_actual_token'")
        # return  # 如果想要强制需要token，可以取消注释这行
    
    # 创建ImageUploader实例
    uploader = ImageUploader(jwt_token=jwt_token)
    
    print("=== 测试 ImageUploader ===\n")
    
    # 测试1: 基本上传（返回fileId）
    print("测试1: 基本上传 (返回fileId)")
    try:
        test_image = create_test_image()
        result = uploader.upload(
            file=test_image,
            filename="test_image.png"
        )
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    print("-" * 50)
    
    # 测试2: 返回URL
    print("测试2: 上传并返回URL")
    try:
        test_image = create_test_image()
        result = uploader.upload(
            file=test_image,
            filename="test_image_url.png",
            return_type="url"
        )
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    print("-" * 50)
    
    # 测试3: 设置最大图片大小
    print("测试3: 设置最大图片大小限制")
    try:
        test_image = create_test_image()
        result = uploader.upload(
            file=test_image,
            filename="test_image_size_limit.png",
            max_picture_size=1024  # 1KB限制
        )
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    print("-" * 50)
    
    # 测试4: 添加元数据
    print("测试4: 添加元数据")
    try:
        test_image = create_test_image()
        metadata = json.dumps({
            "source": "test",
            "quality": "high",
            "description": "测试图片"
        }, ensure_ascii=False)
        
        result = uploader.upload(
            file=test_image,
            filename="test_image_metadata.png",
            metadata=metadata
        )
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    print("-" * 50)
    
    # 测试5: 综合测试（所有参数）
    print("测试5: 综合测试（所有参数）")
    try:
        test_image = create_test_image()
        metadata = json.dumps({
            "test_type": "comprehensive",
            "timestamp": "2024-01-01T12:00:00Z"
        })
        
        result = uploader.upload(
            file=test_image,
            filename="test_comprehensive.png",
            return_type="url",
            max_picture_size=2048,
            metadata=metadata
        )
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"错误: {str(e)}")
    print("-" * 50)

def test_ensure_image_inputs():
    """测试 ensure_image_inputs 批量处理功能"""
    
    jwt_token = os.getenv('AUTOAGENTS_JWT_TOKEN', 'your_test_token_here')
    uploader = ImageUploader(jwt_token=jwt_token)
    
    print("=== 测试 ensure_image_inputs 批量处理 ===\n")
    
    try:
        # 创建多个测试图片
        test_images = []
        for i in range(2):
            img = create_test_image()
            img.name = f"batch_test_{i}.png"
            test_images.append(img)
        
        # 批量上传
        file_inputs = uploader.ensure_image_inputs(
            files=test_images,
            return_type="fileId",
            max_picture_size=1024
        )
        
        print(f"批量上传结果 ({len(file_inputs)} 个文件):")
        for i, file_input in enumerate(file_inputs):
            print(f"  文件{i+1}: fileId={file_input.fileId}, fileName={file_input.fileName}")
            
    except Exception as e:
        print(f"批量上传错误: {str(e)}")

def test_with_real_image():
    """如果有真实图片文件，测试真实图片上传"""
    
    # 检查是否有测试图片
    test_image_path = "playground/test_workspace/test_image.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"跳过真实图片测试: 找不到测试图片 {test_image_path}")
        print("如果要测试真实图片，请将图片文件放到 playground/test_workspace/test_image.jpg")
        return
    
    jwt_token = os.getenv('AUTOAGENTS_JWT_TOKEN', 'your_test_token_here')
    uploader = ImageUploader(jwt_token=jwt_token)
    
    print("=== 测试真实图片上传 ===\n")
    
    try:
        with open(test_image_path, 'rb') as f:
            result = uploader.upload(
                file=f,
                filename="real_test_image.jpg",
                return_type="url"
            )
        print(f"真实图片上传结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"真实图片上传错误: {str(e)}")

def main():
    """主测试函数"""
    print("开始测试 ImageUploader...")
    print("请确保设置了正确的JWT token环境变量: AUTOAGENTS_JWT_TOKEN\n")
    
    # 基本功能测试
    test_image_uploader()
    
    print("\n" + "="*60 + "\n")
    
    # 批量处理测试
    test_ensure_image_inputs()
    
    print("\n" + "="*60 + "\n")
    
    # 真实图片测试
    test_with_real_image()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()