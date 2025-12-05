"""
Tavily Search 工具集成
"""
from typing import Optional
from langchain_community.tools import TavilySearchResults
from config import settings
import os

def create_tavily_tool(max_results: int = 5) -> TavilySearchResults:
    """
    创建 Tavily 搜索工具
    
    Args:
        max_results: 最大返回结果数量
        
    Returns:
        TavilySearchResults: 搜索工具实例
    """
    # 确保 API Key 从环境变量加载
    tavily_key = settings.tavily_api_key or os.getenv("TAVILY_API_KEY")
    
    if not tavily_key:
        raise ValueError("请配置 TAVILY_API_KEY 环境变量")
    
    # 设置环境变量（确保 TavilySearchResults 能读取）
    os.environ["TAVILY_API_KEY"] = tavily_key
    
    return TavilySearchResults(
        max_results=max_results,
    )

def get_search_tools():
    """获取所有搜索工具"""
    return [create_tavily_tool()]

