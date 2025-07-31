import json
import uuid
from copy import deepcopy

from .template_registry import NODE_TEMPLATES
from ..api.GraphApi import create_app_api
from ..types import CreateAppParams


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
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.viewport = {"x": 0, "y": 0, "zoom": 1.0}

    def add_node(self, node_id, module_type, position, inputs=None, outputs=None):
        tpl = deepcopy(NODE_TEMPLATES.get(module_type))
        final_inputs = self.merge_template_io(tpl.get("inputs", []), inputs)
        final_outputs = self.merge_template_io(tpl.get("outputs", []), outputs)
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
        edge = FlowEdge(source, target, source_handle, target_handle)
        self.edges.append(edge)

    def to_json(self):
        return json.dumps({
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "viewport": self.viewport
        }, indent=2, ensure_ascii=False)


    def merge_template_io(self,template_io, custom_io):
        # 参数说明：
        # template_io：模板中inputs或outputs列表，每个元素是一个字段的字典，字段完整
        # custom_io：用户传入的inputs或outputs列表，通常是部分字段，可能只有部分key覆盖

        if not custom_io:
            # 如果用户没有传自定义字段，直接返回模板的完整字段（深拷贝避免修改原数据）
            return deepcopy(template_io)

        merged = []
        # 遍历模板里的所有字段
        for t_item in template_io:
            # 在用户自定义列表中找有没有和当前模板字段 key 一样的字段
            c_item = next((c for c in custom_io if c.get("key") == t_item.get("key")), None)

            if c_item:
                # 找到了用户自定义字段
                merged_item = deepcopy(t_item)  # 先复制模板字段（保证完整结构）
                merged_item.update(c_item)  # 用用户的字段内容覆盖模板字段（例如value、description等被覆盖）
                merged.append(merged_item)
            else:
                # 用户没定义，直接用模板字段完整拷贝
                merged.append(deepcopy(t_item))

        return merged

    def compile(self,data: CreateAppParams) -> None :
        data.appModel=self.to_json()
        if not data.name:
            data.name = "unTitle"
        create_app_api(data)
