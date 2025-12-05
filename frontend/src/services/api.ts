/**
 * API 服务
 */
import axios from 'axios';
import { Session, StreamEvent } from '../types';

// API 基础 URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 流式聊天接口（多 Agent）
 */
export async function* streamChatMulti(
  message: string,
  sessionId?: string
): AsyncGenerator<StreamEvent, void, unknown> {
  const response = await fetch(`${API_BASE_URL}/chat/multi`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      stream: true,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('Response body is null');
  }

  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    // 解码数据
    buffer += decoder.decode(value, { stream: true });

    // 处理 SSE 格式
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('event:')) {
        // 事件类型行
        continue;
      } else if (line.startsWith('data:')) {
        // 数据行
        const data = line.slice(5).trim();
        if (data) {
          try {
            const event = JSON.parse(data);
            yield event as StreamEvent;
          } catch (e) {
            console.error('Parse error:', e, data);
          }
        }
      }
    }
  }
}

/**
 * 流式聊天接口（单 Agent）
 */
export async function* streamChat(
  message: string,
  sessionId?: string
): AsyncGenerator<StreamEvent, void, unknown> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      stream: true,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('Response body is null');
  }

  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    // 解码数据
    buffer += decoder.decode(value, { stream: true });

    // 处理 SSE 格式
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('event:')) {
        // 事件类型行
        continue;
      } else if (line.startsWith('data:')) {
        // 数据行
        const data = line.slice(5).trim();
        if (data) {
          try {
            const event = JSON.parse(data);
            yield event as StreamEvent;
          } catch (e) {
            console.error('Parse error:', e, data);
          }
        }
      }
    }
  }
}

/**
 * 简单聊天接口（非流式）
 */
export async function chatSimple(message: string, sessionId?: string): Promise<any> {
  const response = await apiClient.post('/chat/simple', {
    message,
    session_id: sessionId,
    stream: false,
  });
  return response.data;
}

/**
 * 获取会话列表
 */
export async function getSessions(): Promise<Session[]> {
  const response = await apiClient.get('/sessions');
  return response.data.sessions;
}

/**
 * 获取会话详情
 */
export async function getSession(sessionId: string): Promise<Session> {
  const response = await apiClient.get(`/sessions/${sessionId}`);
  return response.data;
}

/**
 * 创建新会话
 */
export async function createSession(title?: string): Promise<Session> {
  const response = await apiClient.post('/sessions', { title });
  return response.data;
}

/**
 * 删除会话
 */
export async function deleteSession(sessionId: string): Promise<void> {
  await apiClient.delete(`/sessions/${sessionId}`);
}

export default {
  streamChat,
  streamChatMulti,
  chatSimple,
  getSessions,
  getSession,
  createSession,
  deleteSession,
};

