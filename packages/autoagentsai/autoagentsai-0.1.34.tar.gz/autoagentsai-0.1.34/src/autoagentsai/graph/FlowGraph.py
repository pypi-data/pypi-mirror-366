import json
import uuid
from copy import deepcopy
from typing import Optional, List, Dict, Tuple

from .NodeRegistry import NODE_TEMPLATES, merge_template_io
from ..api.GraphApi import create_app_api, process_add_memory_variable
from ..types.GraphTypes import CreateAppParams
from ..utils.convertor import convert_json_to_json_list


class FlowNode:
    def __init__(self, node_id, module_type, position, inputs=None, outputs=None):
        self.id = node_id
        self.type = "custom"
        self.initialized = False
        self.position = position
        self.data = {
            "inputs": inputs or [],
            "outputs": outputs or [],
            "disabled": False,
            "moduleType": module_type,
        }

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "initialized": self.initialized,
            "position": self.position,
            "data": self.data
        }

class FlowEdge:
    def __init__(self, source, target, source_handle="", target_handle=""):
        self.id = str(uuid.uuid4())
        self.type = "custom"
        self.source = source
        self.target = target
        self.sourceHandle = source_handle
        self.targetHandle = target_handle
        self.data = {}
        self.label = ""
        self.animated = False
        self.sourceX = 0
        self.sourceY = 0
        self.targetX = 0
        self.targetY = 0

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "target": self.target,
            "sourceHandle": self.sourceHandle,
            "targetHandle": self.targetHandle,
            "data": self.data,
            "label": self.label,
            "animated": self.animated,
            "sourceX": self.sourceX,
            "sourceY": self.sourceY,
            "targetX": self.targetX,
            "targetY": self.targetY
        }

class FlowGraph:
    def __init__(self, personal_auth_key: str, personal_auth_secret: str, base_url: str = "https://uat.agentspro.cn"):
        """
        初始化 FlowGraph
        
        Args:
            personal_auth_key: 个人认证密钥
            personal_auth_secret: 个人认证密码
            base_url: API 基础URL，默认为 "https://uat.agentspro.cn"
        """
        self.nodes = []
        self.edges = []
        self.viewport = {"x": 0, "y": 0, "zoom": 1.0}
        
        # 保存认证信息
        self.personal_auth_key = personal_auth_key
        self.personal_auth_secret = personal_auth_secret
        self.base_url = base_url

    def add_node(self, node_id, module_type, position, inputs=None, outputs=None):
        tpl = deepcopy(NODE_TEMPLATES.get(module_type))


        if module_type == "addMemoryVariable":
            final_inputs = process_add_memory_variable(tpl.get("inputs", [])[0],inputs)
            final_outputs = []
        else:
            # 转换简洁格式为展开格式
            converted_inputs = convert_json_to_json_list(inputs)
            converted_outputs = convert_json_to_json_list(outputs)
            final_inputs = merge_template_io(tpl.get("inputs", []), converted_inputs)
            final_outputs = merge_template_io(tpl.get("outputs", []), converted_outputs)


        node = FlowNode(
            node_id=node_id,
            module_type=module_type,
            position=position,
            inputs=final_inputs,
            outputs=final_outputs
        )
        node.data["name"]=tpl.get("name")
        node.data["intro"] = tpl.get("intro")
        if tpl.get("category") is not None:
            node.data["category"] = tpl["category"]
        self.nodes.append(node)

    def add_edge(self, source, target, source_handle="", target_handle=""):
        source_handle, target_handle= self._check_and_fix_handle_type(source,target,source_handle,target_handle)
        edge = FlowEdge(source, target, source_handle, target_handle)
        self.edges.append(edge)

    def to_json(self):
        return json.dumps({
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "viewport": self.viewport
        }, indent=2, ensure_ascii=False)

    def compile(self, 
                name: str = "未命名智能体", # 智能体名称
                avatar: str = "https://uat.agentspro.cn/assets/agent/avatar.png", # 头像URL
                intro: Optional[str] = None, # 智能体介绍
                chatAvatar: Optional[str] = None, # 对话头像URL
                shareAble: Optional[bool] = None, # 是否可分享
                guides: Optional[List] = None, # 引导配置
                category: Optional[str] = None, # 分类
                state: Optional[int] = None, # 状态
                prologue: Optional[str] = None, # 开场白
                extJsonObj: Optional[Dict] = None, # 扩展JSON对象
                allowVoiceInput: Optional[bool] = None, # 是否允许语音输入
                autoSendVoice: Optional[bool] = None, # 是否自动发送语音
                **kwargs) -> None: # 其他参数
        """
        编译并创建智能体应用
        """

        data = CreateAppParams(
            name=name,
            avatar=avatar,
            intro=intro,
            chatAvatar=chatAvatar,
            shareAble=shareAble,
            guides=guides,
            appModel=self.to_json(),  # 自动设置工作流JSON
            category=category,
            state=state,
            prologue=prologue,
            extJsonObj=extJsonObj,
            allowVoiceInput=allowVoiceInput,
            autoSendVoice=autoSendVoice,
            **kwargs
        )
        
        create_app_api(data, self.personal_auth_key, self.personal_auth_secret, self.base_url)

    def _check_and_fix_handle_type(self, source: str, target: str, source_handle: str, target_handle: str) -> Tuple[
        str, str]:
        """
        检查 source_handle 与 target_handle 是否类型一致。
        若不一致，则清空 target_handle。
        """
        source_type = self._get_field_type_from_source(source, source_handle)
        target_type = self._get_field_type_from_target(target, target_handle)

        return (
            source_handle,
            target_handle if source_handle and target_handle and source_type == target_type else ""
        )

    def _get_field_type_from_source(self, node_id: str, field_key: str) -> Optional[str]:
        """
        从节点列表中查找 node_id 对应节点的字段类型（valueType）
        """
        for node in self.nodes:
            if node.id == node_id:
                for field in node.data.get("outputs", []):
                    if field.get("key") == field_key:
                        return field.get("valueType")
                break
        return None
    def _get_field_type_from_target(self, node_id: str, field_key: str) -> Optional[str]:
        """
        从节点列表中查找 node_id 对应节点的字段类型（valueType）
        """
        for node in self.nodes:
            if node.id == node_id:
                for field in node.data.get("inputs", []):
                    if field.get("key") == field_key:
                        return field.get("valueType")
                break
        return None
