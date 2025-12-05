"""
多 Agent 协作架构
实现：任务拆解 Agent、信息收集 Agent、报告生成 Agent
"""
from typing import AsyncIterator, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from config import get_llm_config
from tools.tavily_search import get_search_tools
import json

# 任务规划 Agent 提示词
PLANNER_PROMPT = """你是一个专业的研究任务规划专家。

你的职责是：
1. 分析用户的研究需求
2. 将研究任务拆解为多个子任务
3. 为每个子任务制定具体的调研方向

用户问题：{input}

请将任务拆解为 3-5 个具体的子任务，每个子任务应该包括：
- 任务标题
- 调研方向和关键问题
- 预期输出

请以 JSON 格式输出，例如：
```json
{{
  "research_plan": [
    {{
      "task_id": 1,
      "title": "任务标题",
      "directions": ["方向1", "方向2"],
      "expected_output": "预期输出描述"
    }}
  ]
}}
```
"""

# 信息收集 Agent 提示词
RESEARCHER_PROMPT = """你是一个专业的信息收集专家。

你可以使用以下工具进行信息搜索：
{tools}

工具名称: {tool_names}

你的职责是：
1. 根据给定的研究任务，使用搜索工具查找相关信息
2. 对搜索结果进行分析和筛选
3. 提取关键信息和数据
4. 整理成结构化的输出

请使用以下格式：

Question: 研究任务
Thought: 你应该思考要搜索什么
Action: 要使用的工具，应该是 [{tool_names}] 中的一个
Action Input: 工具的输入参数
Observation: 工具返回的结果
... (可以重复多次搜索)
Thought: 我已经收集到足够的信息
Final Answer: 整理后的研究结果（结构化输出）

重要提示：
- 从多个角度搜索信息，确保全面性
- 注意信息的来源和可信度
- 提取关键数据和观点
- 结果要结构化、条理清晰

研究任务：{input}
Thought: {agent_scratchpad}
"""

# 报告生成 Agent 提示词
WRITER_PROMPT = """你是一个专业的研究报告撰写专家。

你的职责是：
1. 综合所有子任务的研究结果
2. 分析和整合信息
3. 撰写一份结构清晰、内容详实的研究报告

报告要求：
- 使用 Markdown 格式
- 包含以下部分：
  * 摘要（Executive Summary）
  * 背景介绍（Background）
  * 详细分析（Detailed Analysis）- 包含各个子主题
  * 关键发现（Key Findings）
  * 结论和展望（Conclusion & Outlook）
- 内容要有理有据，引用具体信息
- 语言专业、客观

研究主题：{topic}

子任务研究结果：
{research_results}

请撰写完整的研究报告：
"""

class MultiAgentResearcher:
    """多 Agent 研究系统"""
    
    def __init__(self):
        """初始化多个 Agent"""
        llm_config = get_llm_config()
        
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=llm_config["model"],
            temperature=llm_config["temperature"],
            api_key=llm_config["api_key"],
            base_url=llm_config["api_base"],
            streaming=True,
        )
        
        # 低温度 LLM（用于规划和写作）
        self.llm_low_temp = ChatOpenAI(
            model=llm_config["model"],
            temperature=0.3,
            api_key=llm_config["api_key"],
            base_url=llm_config["api_base"],
        )
        
        # 获取工具
        self.tools = get_search_tools()
        
        # 初始化各个 Agent
        self._init_agents()
    
    def _init_agents(self):
        """初始化各个子 Agent"""
        
        # 研究员 Agent（带工具）
        researcher_prompt = PromptTemplate.from_template(RESEARCHER_PROMPT)
        researcher_agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=researcher_prompt
        )
        self.researcher_executor = AgentExecutor(
            agent=researcher_agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=8,
        )
    
    async def plan_research(self, query: str) -> List[Dict[str, Any]]:
        """
        规划研究任务
        
        Args:
            query: 用户查询
            
        Returns:
            List[Dict]: 研究任务列表
        """
        try:
            prompt = PLANNER_PROMPT.format(input=query)
            response = await self.llm_low_temp.ainvoke([HumanMessage(content=prompt)])
            
            # 解析 JSON
            content = response.content
            
            # 提取 JSON 部分
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                json_str = content
            
            plan_data = json.loads(json_str)
            return plan_data.get("research_plan", [])
            
        except Exception as e:
            print(f"Plan research error: {e}")
            # 返回默认计划
            return [
                {
                    "task_id": 1,
                    "title": "深度研究：" + query,
                    "directions": ["全面搜索相关信息"],
                    "expected_output": "详细研究结果"
                }
            ]
    
    async def research_task(self, task: Dict[str, Any]) -> str:
        """
        执行单个研究任务
        
        Args:
            task: 任务信息
            
        Returns:
            str: 研究结果
        """
        try:
            # 构建研究查询
            query = f"{task['title']}\n"
            query += f"调研方向：{', '.join(task['directions'])}\n"
            query += f"预期输出：{task['expected_output']}"
            
            # 执行研究
            result = await self.researcher_executor.ainvoke({"input": query})
            return result.get("output", "")
            
        except Exception as e:
            print(f"Research task error: {e}")
            return f"任务执行出错：{str(e)}"
    
    async def generate_report(self, topic: str, research_results: List[Dict[str, Any]]) -> str:
        """
        生成研究报告
        
        Args:
            topic: 研究主题
            research_results: 各子任务的研究结果
            
        Returns:
            str: 完整报告
        """
        try:
            # 整理研究结果
            results_text = ""
            for i, result in enumerate(research_results, 1):
                results_text += f"\n## 子任务 {i}: {result['task']['title']}\n"
                results_text += f"{result['result']}\n"
            
            # 生成报告
            prompt = WRITER_PROMPT.format(
                topic=topic,
                research_results=results_text
            )
            
            response = await self.llm_low_temp.ainvoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            print(f"Generate report error: {e}")
            return f"报告生成出错：{str(e)}"
    
    async def astream(self, query: str) -> AsyncIterator[Dict[str, Any]]:
        """
        流式执行完整的多 Agent 研究流程
        
        Args:
            query: 用户查询
            
        Yields:
            Dict[str, Any]: 流式事件
        """
        try:
            # 步骤 1: 规划任务
            yield {
                "type": "thinking",
                "content": "🎯 正在规划研究任务...",
                "metadata": {"step": "planning"}
            }
            
            tasks = await self.plan_research(query)
            
            yield {
                "type": "agent_action",
                "content": {
                    "action": "plan_created",
                    "tasks": tasks
                },
                "metadata": {"step": "planning", "task_count": len(tasks)}
            }
            
            # 步骤 2: 执行各个子任务
            research_results = []
            
            for i, task in enumerate(tasks, 1):
                yield {
                    "type": "thinking",
                    "content": f"📚 正在执行子任务 {i}/{len(tasks)}: {task['title']}",
                    "metadata": {"step": "researching", "task_id": task['task_id']}
                }
                
                # 执行研究任务（流式输出工具调用）
                result = await self.research_task(task)
                
                research_results.append({
                    "task": task,
                    "result": result
                })
                
                yield {
                    "type": "agent_action",
                    "content": {
                        "action": "task_completed",
                        "task_id": task['task_id'],
                        "title": task['title']
                    },
                    "metadata": {"step": "researching"}
                }
            
            # 步骤 3: 生成报告
            yield {
                "type": "thinking",
                "content": "✍️ 正在撰写研究报告...",
                "metadata": {"step": "writing"}
            }
            
            report = await self.generate_report(query, research_results)
            
            # 输出报告（逐段流式输出）
            paragraphs = report.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    yield {
                        "type": "text",
                        "content": paragraph + "\n\n",
                        "metadata": {"step": "output"}
                    }
            
            # 完成
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

