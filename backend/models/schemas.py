"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime

class Message(BaseModel):
    """消息模型"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话 ID")
    stream: bool = Field(True, description="是否流式响应")

class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

class StreamEvent(BaseModel):
    """流式事件"""
    type: Literal["text", "tool_call", "tool_result", "agent_action", "thinking", "error", "done"]
    content: Any
    metadata: Optional[Dict[str, Any]] = None

class Session(BaseModel):
    """会话模型"""
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
    
class SessionCreate(BaseModel):
    """创建会话"""
    title: Optional[str] = "新对话"

class SessionList(BaseModel):
    """会话列表"""
    sessions: List[Session]
    total: int

