"""
基础 Agent 实现
"""
from typing import AsyncIterator, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from config import get_llm_config
from tools.tavily_search import get_search_tools
import json

# ReAct 提示词模板
REACT_PROMPT = """你是一个专业的研究助手，能够帮助用户深度研究指定话题并输出详细报告。

你可以使用以下工具:
{tools}

工具名称: {tool_names}

请使用以下格式进行思考和行动:

Question: 用户的问题
Thought: 你应该思考要做什么
Action: 要使用的工具，应该是 [{tool_names}] 中的一个
Action Input: 工具的输入参数
Observation: 工具返回的结果
... (这个 Thought/Action/Action Input/Observation 过程可以重复多次)
Thought: 我现在知道最终答案了
Final Answer: 对用户问题的最终回答

重要提示:
- 在搜索信息时，要多角度、多维度地搜索，确保信息全面
- 对搜索结果要进行分析和总结
- 最终报告要结构清晰、内容详实、有理有据
- 如果需要搜索多个相关主题，请分步进行

开始!

Question: {input}
Thought: {agent_scratchpad}
"""

class BaseResearchAgent:
    """基础研究 Agent"""
    
    def __init__(self):
        """初始化 Agent"""
        llm_config = get_llm_config()
        
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=llm_config["model"],
            temperature=llm_config["temperature"],
            api_key=llm_config["api_key"],
            base_url=llm_config["api_base"],
            streaming=True,
        )
        
        # 获取工具
        self.tools = get_search_tools()
        
        # 创建提示词
        self.prompt = PromptTemplate.from_template(REACT_PROMPT)
        
        # 创建 Agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # 创建 Agent 执行器
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
        )
    
    async def astream(self, query: str, session_history: List[Dict[str, str]] = None) -> AsyncIterator[Dict[str, Any]]:
        """
        异步流式执行 Agent
        
        Args:
            query: 用户查询
            session_history: 会话历史
            
        Yields:
            Dict[str, Any]: 流式事件
        """
        try:
            # 构建输入
            inputs = {"input": query}
            
            # 流式执行
            async for event in self.agent_executor.astream_events(inputs, version="v1"):
                event_type = event.get("event")
                
                # 处理不同类型的事件
                if event_type == "on_chat_model_stream":
                    # LLM 输出流
                    content = event["data"]["chunk"].content
                    if content:
                        yield {
                            "type": "text",
                            "content": content,
                            "metadata": {}
                        }
                
                elif event_type == "on_tool_start":
                    # 工具开始调用
                    tool_name = event["name"]
                    tool_input = event["data"].get("input", {})
                    yield {
                        "type": "tool_call",
                        "content": {
                            "tool": tool_name,
                            "input": tool_input
                        },
                        "metadata": {}
                    }
                
                elif event_type == "on_tool_end":
                    # 工具调用结束
                    tool_name = event["name"]
                    tool_output = event["data"].get("output")
                    yield {
                        "type": "tool_result",
                        "content": {
                            "tool": tool_name,
                            "output": tool_output
                        },
                        "metadata": {}
                    }
                
                elif event_type == "on_agent_action":
                    # Agent 行动
                    action = event["data"]["action"]
                    yield {
                        "type": "agent_action",
                        "content": {
                            "tool": action.tool,
                            "tool_input": action.tool_input,
                            "log": action.log
                        },
                        "metadata": {}
                    }
            
            # 发送完成事件
            yield {
                "type": "done",
                "content": "completed",
                "metadata": {}
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "content": str(e),
                "metadata": {}
            }
    
    async def ainvoke(self, query: str, session_history: List[Dict[str, str]] = None) -> str:
        """
        异步非流式执行 Agent
        
        Args:
            query: 用户查询
            session_history: 会话历史
            
        Returns:
            str: Agent 响应
        """
        try:
            inputs = {"input": query}
            result = await self.agent_executor.ainvoke(inputs)
            return result.get("output", "")
        except Exception as e:
            return f"执行出错: {str(e)}"

