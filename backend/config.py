"""
配置管理
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    
    # API 配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LLM 配置
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"
    volc_api_key: Optional[str] = None
    volc_api_base: Optional[str] = None
    
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.7
    
    # Tavily Search 配置
    tavily_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局配置实例
settings = Settings()

def get_llm_config():
    """获取 LLM 配置"""
    if settings.openai_api_key:
        return {
            "type": "openai",
            "api_key": settings.openai_api_key,
            "api_base": settings.openai_api_base,
            "model": settings.llm_model,
            "temperature": settings.llm_temperature
        }
    elif settings.volc_api_key:
        return {
            "type": "volc",
            "api_key": settings.volc_api_key,
            "api_base": settings.volc_api_base,
            "model": settings.llm_model,
            "temperature": settings.llm_temperature
        }
    else:
        raise ValueError("请配置 OPENAI_API_KEY 或 VOLC_API_KEY")

