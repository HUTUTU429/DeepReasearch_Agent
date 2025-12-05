# DeepResearch Agent

一个功能完整的深度研究 AI Agent 系统，基于 LangChain 和 React 构建。

## ⭐ 项目亮点

实现了一个简化版的 DeepResearch Agent。主要功能是通过 AI Agent 自动规划任务、搜索信息并生成研究报告。

整个项目花了大概 3-4 周时间，从零开始学习 LangChain 和 Agent 开发，踩了不少坑，但收获也很多。

## 主要功能

- **多 Agent 协作**：实现了任务规划、信息收集和报告生成三个 Agent
- **实时流式输出**：可以看到 AI 的思考过程，体验比较好
- **网络搜索集成**：接入了 Tavily API，能够搜索最新的信息
- **会话管理**：支持多个对话同时进行
- **前端界面**：用 React + TypeScript 写的，界面还算清爽

## 技术栈

**后端：**
- Python + FastAPI
- LangChain（Agent 框架）
- OpenAI API / 火山引擎 API
- Tavily Search API

**前端：**
- React 18 + TypeScript
- Ant Design（UI 组件）
- SSE 流式通信

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- OpenAI 或火山引擎的 API Key
- Tavily API Key（用于搜索）

### 安装步骤

**1. 后端启动**

**1. 后端启动**

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置 API Keys
cp .env.example .env
# 编辑 .env 文件，填入你的 API Keys

# 启动
python main.py
```

**2. 前端启动**（新开一个终端）

```bash
cd frontend
npm install
npm start
```

浏览器会自动打开 `http://localhost:3000`

## 项目结构

## 项目结构

```
backend/          # 后端 Python 代码
├── agents/       # Agent 实现
├── api/          # FastAPI 路由
├── models/       # 数据模型
├── tools/        # 工具集成（Tavily搜索）
└── main.py       # 入口文件

frontend/         # 前端 React 代码
├── src/
│   ├── components/  # 组件
│   ├── pages/       # 页面
│   ├── services/    # API调用
│   └── types/       # TypeScript类型
└── package.json
```

## 开发过程

### 第一周：调研学习
- 研究了 LangChain、AutoGPT 等 Agent 框架
- 学习 ReAct 范式和 Plan-and-Execute 模式
- 确定技术方案

### 第一周：调研学习
- 研究了 LangChain、AutoGPT 等 Agent 框架
- 学习 ReAct 范式和 Plan-and-Execute 模式
- 确定技术方案

### 第二周：基础功能
- 搭建 FastAPI 后端框架
- 实现单 Agent 基础功能
- 集成 Tavily 搜索 API
- 完成前端基础页面

### 第三周：核心开发
- 实现多 Agent 协作机制
- 添加流式响应（这块调试了很久）
- 完成消息类型的渲染
- 实现会话管理

### 第四周：优化完善
- 修复各种 bug
- 优化用户体验
- 添加 Docker 支持
- 编写文档

## 遇到的问题

1. **LangChain 版本问题**
   - 依赖包版本冲突，最后通过放宽版本限制解决
   
2. **流式响应实现**
   - SSE 在浏览器中的兼容性问题，花了时间研究事件解析
   
3. **TypeScript 类型定义**
   - 刚开始对 TypeScript 不太熟悉，慢慢学会了泛型和类型推断
   
4. **API 配额限制**
   - OpenAI API 用完了免费额度，后来改用火山引擎

## 功能演示

**单 Agent 模式示例：**
```
输入：什么是人工智能？
输出：快速给出定义和基本概念
```

**多 Agent 模式示例：**
```
输入：分析2025年人工智能发展趋势
过程：
  1. 规划 Agent 拆解任务
  2. 研究 Agent 搜索信息
  3. 写作 Agent 生成报告
输出：完整的研究报告（Markdown格式）
```

## 部署说明

### Docker 部署（推荐）

```bash
# 配置环境变量
cp backend/.env.example backend/.env

# 启动
docker-compose up -d
```

### 手动部署

参考上面的"快速开始"部分


## 学习收获

1. **Agent 开发**：深入理解了 ReAct、Plan-and-Execute 等范式
2. **流式编程**：学会了 SSE 和异步编程
3. **TypeScript**：提升了类型系统的理解
4. **系统设计**：学会了如何设计一个完整的前后端分离项目

## 参考资料

- LangChain 官方文档
- OpenAI DeepResearch 
- Perplexity AI
- AutoGPT 项目

## 致谢

感谢字节跳动训练营提供的学习机会！

---

如有问题欢迎提 Issue 讨论 ~

