from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class AgentGuide(BaseModel):
    indexNum: Optional[int] = None
    guide: Optional[str] = None


class CreateAppParams(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    chatAvatar: Optional[str] = None
    intro: Optional[str] = None
    shareAble: Optional[bool] = None
    guides: Optional[List[AgentGuide]] = None
    appModel: Optional[str] = None
    category: Optional[str] = None
    state: Optional[int] = None
    prologue: Optional[str] = None
    extJsonObj: Optional[Dict[str, Any]] = None
    allowVoiceInput: Optional[bool] = None
    autoSendVoice: Optional[bool] = None
    updateAt: Optional[datetime] = None