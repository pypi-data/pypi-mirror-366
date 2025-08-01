from typing import Optional, List
from pydantic import BaseModel, Field


class KbSearchConfig(BaseModel):
    """向量搜索配置"""
    vectorSimilarLimit: Optional[float] = None
    vectorSimilarWeight: Optional[float] = None
    topK: Optional[int] = None
    enableRerank: Optional[bool] = None
    rerankModelType: Optional[str] = None
    rerankSimilarLimit: Optional[float] = None
    rerankTopK: Optional[int] = None


class KbExtConfig(BaseModel):
    """知识库扩展配置"""
    configWay: Optional[str] = None
    chunkSize: Optional[int] = None
    coverageRate: Optional[float] = None
    similarity: Optional[float] = None
    limit: Optional[int] = None
    agentId: Optional[int] = None
    language: Optional[str] = None
    parserType: Optional[str] = None
    contentEnhances: Optional[List[str]] = Field(default_factory=list)
    search: Optional[KbSearchConfig] = None


class KbCreateRequest(BaseModel):
    """创建知识库请求模型"""
    parentId: Optional[int] = 0
    name: Optional[str] = ""
    description: Optional[str] = ""
    avatarUrl: Optional[str] = ""
    vectorModel: Optional[str] = ""
    type: Optional[str] = "kb"  # "folder" 或 "kb"
    tags: Optional[List[str]] = Field(default_factory=list)
    ext: Optional[KbExtConfig] = None


class KbModifyRequest(BaseModel):
    """修改知识库请求模型"""
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    avatarUrl: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    ext: Optional[KbExtConfig] = None


class KbQueryRequest(BaseModel):
    """知识库列表查询请求模型"""
    pageNum: Optional[int] = 1
    pageSize: Optional[int] = 10
    count: Optional[bool] = True
    keywords: Optional[str] = ""
    parentId: Optional[int] = 0
    scope: Optional[int] = 0
    externalParams: Optional[dict] = Field(default_factory=dict)

