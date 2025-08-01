import requests
import os
import mimetypes
from typing import Optional, Dict, Union, IO, List
from io import BytesIO
from ..types.ChatTypes import FileInput, ImageInput


class FileUploader:
    def __init__(self, jwt_token: str, base_url: str = "https://uat.agentspro.cn"):
        """
        AutoAgents AI 文件上传器
        
        负责将本地文件上传到 AutoAgents 平台，并获取文件 ID 用于后续的对话引用。
        支持多种文件类型的自动识别和上传。
        
        Args:
            jwt_token (str): JWT 认证令牌
                
            base_url (str, optional): API 服务基础地址
                - 可选参数，默认为 "https://uat.agentspro.cn"  
                - 测试环境: "https://uat.agentspro.cn"
                - 生产环境: "https://agentspro.cn"
                - 私有部署时可指定自定义地址
        """
        self.jwt_token = jwt_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {jwt_token}"
        }

    def upload(self, file: IO, filename: str = "uploaded_file") -> Dict:
        url = f"{self.base_url}/api/fs/upload"
        
        # 根据文件扩展名自动检测MIME类型
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type is None:
            mime_type = 'application/octet-stream'  # 默认类型
        
        print(f"Debug: 上传文件 {filename}, 检测到MIME类型: {mime_type}")
        
        files = [
            ('file', (filename, file, mime_type))
        ]
        
        payload = {}
        
        try:
            response = requests.post(url, headers=self.headers, data=payload, files=files, timeout=30)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('code') == 1:  # 成功
                        file_id = result["data"]
                        return {
                            "fileId": file_id,
                            "fileName": filename,
                            "fileType": mime_type,
                            "fileUrl": "",  # 当前API不返回URL
                            "success": True
                        }
                    else:  # 失败
                        error_msg = result.get('msg', '未知错误')
                        raise Exception(f"API返回错误: {error_msg}")
                        
                except Exception as e:
                    # 如果不是JSON响应，返回错误信息字典
                    print(f"Debug: 非JSON响应，返回原始文本: {response.text}")
                    return {
                        "fileId": "",
                        "fileName": filename,
                        "fileType": mime_type,
                        "fileUrl": "",
                        "success": False,
                        "error": response.text.strip()
                    }
            else:
                raise Exception(f"Upload failed: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"File upload error: {str(e)}")

    def ensure_file_inputs(self, files: Optional[List[Union[str, IO]]] = None) -> List[FileInput]:
        file_inputs = []
        if not files:
            return file_inputs

        for f in files:
            if isinstance(f, str):
                # 检查字符串是否是文件路径
                if os.path.exists(f) or '.' in os.path.basename(f):
                    # 如果文件存在或包含文件扩展名，当作文件路径处理
                    try:
                        file_obj = create_file_like(f)
                        filename = os.path.basename(f)
                        upload_result = self.upload(file_obj, filename=filename)
                        print(f"Debug: 上传文件 {filename}, 结果: {upload_result}")
                        
                        if upload_result.get("success", False):
                            file_inputs.append(FileInput(
                                fileId=upload_result["fileId"],
                                fileName=upload_result["fileName"],
                                fileType=upload_result["fileType"],
                                fileUrl=upload_result["fileUrl"]
                            ))
                        else:
                            print(f"Warning: 文件上传失败: {upload_result.get('error', '未知错误')}")
                    except Exception as e:
                        print(f"Warning: 处理文件路径 {f} 时出错: {str(e)}")
                else:
                    # 如果不是文件路径，假设它是 fileId，创建一个基本的 FileInput
                    file_inputs.append(FileInput(
                        fileId=f,
                        fileName="",  # 无法从 fileId 推断文件名
                        fileType="",
                        fileUrl=""
                    ))
            else:
                # 尝试获取文件名，优先使用 filename 属性，然后是 name 属性
                filename = getattr(f, "filename", None)
                if filename is None:
                    filename = getattr(f, "name", "uploaded_file")
                    if filename != "uploaded_file":
                        # 从完整路径中提取文件名
                        filename = os.path.basename(filename)
                
                upload_result = self.upload(f, filename=filename)
                print(f"Debug: 上传文件 {filename}, 结果: {upload_result}")
                
                if upload_result.get("success", False):
                    file_inputs.append(FileInput(
                        fileId=upload_result["fileId"],
                        fileName=upload_result["fileName"],
                        fileType=upload_result["fileType"],
                        fileUrl=upload_result["fileUrl"]
                    ))
                else:
                    # 上传失败，但仍创建一个 FileInput 对象以保持一致性
                    print(f"Warning: 文件上传失败: {upload_result.get('error', '未知错误')}")

        return file_inputs


class ImageUploader:
    def __init__(self, jwt_token: str, base_url: str = "https://uat.agentspro.cn"):
        """
        AutoAgents AI 图片上传器
        
        负责将图片文件上传到 AutoAgents 平台并进行压缩处理，支持返回文件ID或URL。
        专门针对图片文件优化，支持大小限制和元数据扩展。
        
        Args:
            jwt_token (str): JWT 认证令牌
                
            base_url (str, optional): API 服务基础地址
                - 可选参数，默认为 "https://uat.agentspro.cn"  
                - 测试环境: "https://uat.agentspro.cn"
                - 生产环境: "https://agentspro.cn"
                - 私有部署时可指定自定义地址
        """
        self.jwt_token = jwt_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {jwt_token}"
        }

    def upload(self, 
               file: IO, 
               filename: str = "uploaded_image", 
               return_type: str = "fileId", 
               max_picture_size: Optional[int] = None,
               metadata: Optional[str] = None) -> Dict:
        """
        上传并压缩图片
        
        Args:
            file (IO): 图片文件对象
            filename (str): 文件名，默认为 "uploaded_image"
            return_type (str): 返回类型，"fileId"(默认) 或 "url"
            max_picture_size (int, optional): 最大图片大小限制
            metadata (str, optional): 扩展数据，JSON字符串格式
            
        Returns:
            Dict: 上传结果，包含文件信息或错误信息
        """
        url = f"{self.base_url}/api/fs/uploadAndResizePic"
        
        # 根据文件扩展名自动检测MIME类型
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type is None:
            mime_type = 'application/octet-stream'  # 默认类型
        
        print(f"Debug: 上传图片 {filename}, 检测到MIME类型: {mime_type}")
        
        files = [
            ('file', (filename, file, mime_type))
        ]
        
        # 构建请求数据
        payload = {
            'returnType': return_type
        }
        
        if max_picture_size is not None:
            payload['maxPictureSize'] = str(max_picture_size)
            
        if metadata is not None:
            payload['metadata'] = metadata
        
        try:
            response = requests.post(url, headers=self.headers, data=payload, files=files, timeout=30)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('code') == 1:  # 成功
                        data = result["data"]
                        
                        if return_type == "url":
                            return {
                                "fileId": "",
                                "fileName": filename,
                                "fileType": mime_type,
                                "fileUrl": data,  # URL形式返回
                                "success": True,
                                "returnType": return_type
                            }
                        else:  # fileId
                            return {
                                "fileId": data,  # fileId形式返回
                                "fileName": filename,
                                "fileType": mime_type,
                                "fileUrl": "",
                                "success": True,
                                "returnType": return_type
                            }
                    else:  # 失败
                        error_msg = result.get('msg', '未知错误')
                        raise Exception(f"API返回错误: {error_msg}")
                        
                except Exception as e:
                    # 如果不是JSON响应，返回错误信息字典
                    print(f"Debug: 非JSON响应，返回原始文本: {response.text}")
                    return {
                        "fileId": "",
                        "fileName": filename,
                        "fileType": mime_type,
                        "fileUrl": "",
                        "success": False,
                        "error": response.text.strip(),
                        "returnType": return_type
                    }
            else:
                raise Exception(f"Image upload failed: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"Image upload error: {str(e)}")

    def ensure_image_inputs(self, images: Optional[List[Union[str, IO]]] = None, **kwargs) -> List[ImageInput]:
        """
        确保图片输入格式正确，支持URL字符串和本地文件路径
        
        Args:
            images: 图片列表，可以是URL字符串、文件路径字符串或文件对象
            **kwargs: 传递给upload方法的额外参数（return_type, max_picture_size, metadata）
            
        Returns:
            List[ImageInput]: 处理后的图片输入列表
        """
        image_inputs = []
        if not images:
            return image_inputs

        # 确保返回URL格式
        kwargs.setdefault('return_type', 'url')

        for image in images:
            if isinstance(image, str):
                if image.startswith(('http://', 'https://')):
                    # 直接是URL，转换为ImageInput
                    image_inputs.append(ImageInput(url=image))
                else:
                    # 本地文件路径，先上传获取URL
                    if os.path.exists(image):
                        try:
                            with open(image, 'rb') as f:
                                result = self.upload(
                                    file=f,
                                    filename=os.path.basename(image),
                                    **kwargs
                                )
                                if result.get("success") and result.get("fileUrl"):
                                    image_inputs.append(ImageInput(url=result["fileUrl"]))
                                else:
                                    print(f"Warning: 图片上传失败: {image}")
                        except Exception as e:
                            print(f"Warning: 处理图片文件失败 {image}: {e}")
                    else:
                        print(f"Warning: 图片文件不存在: {image}")
            else:
                # 文件对象，上传后获取URL
                try:
                    filename = getattr(image, "filename", None)
                    if filename is None:
                        filename = getattr(image, "name", "uploaded_image")
                        if filename != "uploaded_image":
                            filename = os.path.basename(filename)
                    
                    result = self.upload(image, filename=filename, **kwargs)
                    if result.get("success") and result.get("fileUrl"):
                        image_inputs.append(ImageInput(url=result["fileUrl"]))
                    else:
                        print(f"Warning: 图片上传失败: {filename}")
                except Exception as e:
                    print(f"Warning: 处理图片文件对象失败: {e}")

        return image_inputs


def create_file_like(file_input, filename: Optional[str] = None):
    # 处理不同类型的输入
    if isinstance(file_input, str):
        # 文件路径
        with open(file_input, "rb") as f:
            file_content = f.read()
        
        file_like = BytesIO(file_content)
        file_like.name = file_input.split("/")[-1]
        return file_like
        
    elif isinstance(file_input, bytes):
        # 原始字节数据
        file_like = BytesIO(file_input)
        file_like.name = filename or "uploaded_file"
        return file_like
        
    elif isinstance(file_input, BytesIO):
        # 已经是 BytesIO 对象
        if not hasattr(file_input, 'name') or not file_input.name:
            file_input.name = filename or "uploaded_file"
        return file_input
        
    elif hasattr(file_input, 'read'):
        # 文件对象或类文件对象（包括前端上传的文件）
        try:
            # 尝试读取内容
            content = file_input.read()
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            file_like = BytesIO(content)
            
            # 确定文件名的优先级
            if filename:
                file_like.name = filename
            elif hasattr(file_input, 'filename') and file_input.filename:
                file_like.name = file_input.filename
            elif hasattr(file_input, 'name') and file_input.name:
                file_like.name = os.path.basename(file_input.name)
            else:
                file_like.name = "uploaded_file"
                
            return file_like
            
        except Exception as e:
            raise ValueError(f"无法读取文件对象: {str(e)}")
            
    else:
        raise TypeError(f"不支持的文件输入类型: {type(file_input)}")
