"""
API 路由定义
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from typing import Dict, List
import json
import uuid
from datetime import datetime

from models.schemas import (
    ChatRequest, ChatResponse, StreamEvent,
    Session, SessionCreate, SessionList, Message
)
from agents.base_agent import BaseResearchAgent
from agents.multi_agent import MultiAgentResearcher

router = APIRouter()

# 简单的内存存储（生产环境应该使用数据库）
sessions_db: Dict[str, Session] = {}

# Agent 实例（单例）
agent = BaseResearchAgent()
multi_agent = MultiAgentResearcher()

@router.post("/chat/multi", response_class=EventSourceResponse)
async def chat_multi_agent(request: ChatRequest):
    """
    多 Agent 研究接口 - 支持流式响应
    
    Args:
        request: 聊天请求
        
    Returns:
        StreamingResponse: SSE 流式响应
    """
    try:
        # 获取或创建会话
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id not in sessions_db:
            sessions_db[session_id] = Session(
                session_id=session_id,
                title=request.message[:50],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                messages=[]
            )
        
        session = sessions_db[session_id]
        
        # 添加用户消息
        user_message = Message(
            role="user",
            content=request.message,
            timestamp=datetime.now()
        )
        session.messages.append(user_message)
        
        # 流式响应生成器
        async def event_generator():
            """生成 SSE 事件"""
            try:
                # 发送会话 ID
                yield {
                    "event": "session",
                    "data": json.dumps({"session_id": session_id})
                }
                
                # 收集完整响应
                full_response = ""
                
                # 流式执行多 Agent
                async for event in multi_agent.astream(request.message):
                    # 发送事件
                    yield {
                        "event": event["type"],
                        "data": json.dumps(event, ensure_ascii=False)
                    }
                    
                    # 收集文本内容
                    if event["type"] == "text":
                        full_response += event["content"]
                
                # 保存助手消息
                assistant_message = Message(
                    role="assistant",
                    content=full_response,
                    timestamp=datetime.now()
                )
                session.messages.append(assistant_message)
                session.updated_at = datetime.now()
                
            except Exception as e:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)}, ensure_ascii=False)
                }
        
        return EventSourceResponse(event_generator())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_class=EventSourceResponse)
async def chat(request: ChatRequest):
    """
    单 Agent 聊天接口 - 支持流式响应
    
    Args:
        request: 聊天请求
        
    Returns:
        StreamingResponse: SSE 流式响应
    """
    try:
        # 获取或创建会话
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id not in sessions_db:
            sessions_db[session_id] = Session(
                session_id=session_id,
                title=request.message[:50],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                messages=[]
            )
        
        session = sessions_db[session_id]
        
        # 添加用户消息
        user_message = Message(
            role="user",
            content=request.message,
            timestamp=datetime.now()
        )
        session.messages.append(user_message)
        
        # 流式响应生成器
        async def event_generator():
            """生成 SSE 事件"""
            try:
                # 发送会话 ID
                yield {
                    "event": "session",
                    "data": json.dumps({"session_id": session_id})
                }
                
                # 收集完整响应
                full_response = ""
                
                # 流式执行 Agent
                async for event in agent.astream(request.message):
                    # 发送事件
                    yield {
                        "event": event["type"],
                        "data": json.dumps(event, ensure_ascii=False)
                    }
                    
                    # 收集文本内容
                    if event["type"] == "text":
                        full_response += event["content"]
                
                # 保存助手消息
                assistant_message = Message(
                    role="assistant",
                    content=full_response,
                    timestamp=datetime.now()
                )
                session.messages.append(assistant_message)
                session.updated_at = datetime.now()
                
            except Exception as e:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)}, ensure_ascii=False)
                }
        
        return EventSourceResponse(event_generator())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/simple", response_model=ChatResponse)
async def chat_simple(request: ChatRequest):
    """
    简单聊天接口 - 非流式响应（用于测试）
    
    Args:
        request: 聊天请求
        
    Returns:
        ChatResponse: 聊天响应
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # 执行 Agent
        response = await agent.ainvoke(request.message)
        
        return ChatResponse(
            session_id=session_id,
            message=response,
            metadata={}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=SessionList)
async def get_sessions():
    """
    获取所有会话列表
    
    Returns:
        SessionList: 会话列表
    """
    sessions = list(sessions_db.values())
    sessions.sort(key=lambda x: x.updated_at, reverse=True)
    
    return SessionList(
        sessions=sessions,
        total=len(sessions)
    )

@router.get("/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """
    获取指定会话详情
    
    Args:
        session_id: 会话 ID
        
    Returns:
        Session: 会话详情
    """
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return sessions_db[session_id]

@router.post("/sessions", response_model=Session)
async def create_session(request: SessionCreate):
    """
    创建新会话
    
    Args:
        request: 创建会话请求
        
    Returns:
        Session: 新会话
    """
    session_id = str(uuid.uuid4())
    session = Session(
        session_id=session_id,
        title=request.title,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        messages=[]
    )
    sessions_db[session_id] = session
    
    return session

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    删除指定会话
    
    Args:
        session_id: 会话 ID
        
    Returns:
        Dict: 操作结果
    """
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    del sessions_db[session_id]
    
    return {"message": "会话已删除", "session_id": session_id}

