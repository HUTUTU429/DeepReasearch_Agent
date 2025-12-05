/**
 * 类型定义
 */

// 消息角色
export type MessageRole = 'user' | 'assistant' | 'system';

// 流式事件类型
export type StreamEventType = 
  | 'text' 
  | 'tool_call' 
  | 'tool_result' 
  | 'agent_action' 
  | 'thinking' 
  | 'error' 
  | 'done'
  | 'session';

// 消息接口
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
  events?: StreamEvent[]; // 流式事件记录
}

// 流式事件
export interface StreamEvent {
  type: StreamEventType;
  content: any;
  metadata?: Record<string, any>;
}

// 会话接口
export interface Session {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

// 工具调用信息
export interface ToolCall {
  tool: string;
  input: any;
}

// 工具结果信息
export interface ToolResult {
  tool: string;
  output: any;
}

// Agent 行动信息
export interface AgentAction {
  tool: string;
  tool_input: any;
  log: string;
}

