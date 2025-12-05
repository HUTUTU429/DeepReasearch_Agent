/**
 * 聊天页面
 */
import React, { useState, useRef, useEffect } from 'react';
import { Layout, Spin, message as antMessage, Drawer, Button, Switch } from 'antd';
import { MenuOutlined } from '@ant-design/icons';
import { v4 as uuidv4 } from 'uuid';
import MessageItem from '../components/MessageItem';
import ChatInput from '../components/ChatInput';
import SessionList from '../components/SessionList';
import ThinkingIndicator from '../components/ThinkingIndicator';
import { Message, StreamEvent, Session } from '../types';
import { streamChat, streamChatMulti, getSessions, createSession, deleteSession } from '../services/api';
import './ChatPage.css';

const { Header, Content, Sider } = Layout;

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [useMultiAgent, setUseMultiAgent] = useState(true); // 默认使用多 Agent
  const [thinkingStep, setThinkingStep] = useState<{
    step: 'planning' | 'researching' | 'writing';
    message: string;
  } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 加载会话列表
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const sessionList = await getSessions();
      setSessions(sessionList);
    } catch (error) {
      console.error('Load sessions error:', error);
    }
  };

  const handleSelectSession = (id: string) => {
    const session = sessions.find((s) => s.session_id === id);
    if (session) {
      setSessionId(id);
      setMessages(session.messages as Message[]);
      setDrawerVisible(false);
    }
  };

  const handleCreateSession = async () => {
    try {
      const newSession = await createSession('新对话');
      setSessions([newSession, ...sessions]);
      setSessionId(newSession.session_id);
      setMessages([]);
      setDrawerVisible(false);
    } catch (error) {
      console.error('Create session error:', error);
      antMessage.error('创建会话失败');
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await deleteSession(id);
      setSessions(sessions.filter((s) => s.session_id !== id));
      if (sessionId === id) {
        setSessionId(undefined);
        setMessages([]);
      }
      antMessage.success('会话已删除');
    } catch (error) {
      console.error('Delete session error:', error);
      antMessage.error('删除会话失败');
    }
  };

  // 处理发送消息
  const handleSendMessage = async (content: string) => {
    // 添加用户消息
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 创建助手消息
      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        events: [],
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // 流式接收响应
      let fullContent = '';
      const events: StreamEvent[] = [];

      // 选择使用单 Agent 或多 Agent
      const streamFunc = useMultiAgent ? streamChatMulti : streamChat;

      for await (const event of streamFunc(content, sessionId)) {
        // 处理会话 ID
        if (event.type === 'session') {
          const sessionData = event.content as { session_id?: string };
          if (sessionData.session_id) {
            setSessionId(sessionData.session_id);
          }
          continue;
        }

        // 处理思考过程
        if (event.type === 'thinking') {
          const step = event.metadata?.step as 'planning' | 'researching' | 'writing';
          setThinkingStep({
            step: step || 'planning',
            message: event.content,
          });
        }

        // 处理文本内容
        if (event.type === 'text') {
          fullContent += event.content;
          setThinkingStep(null); // 清除思考指示器
          
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.role === 'assistant') {
              lastMessage.content = fullContent;
            }
            return newMessages;
          });
        }

        // 记录所有事件
        events.push(event);

        // 更新事件记录
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage && lastMessage.role === 'assistant') {
            lastMessage.events = events;
          }
          return newMessages;
        });

        // 处理完成
        if (event.type === 'done') {
          break;
        }

        // 处理错误
        if (event.type === 'error') {
          antMessage.error(`发生错误: ${event.content}`);
          break;
        }
      }

    } catch (error) {
      console.error('Send message error:', error);
      antMessage.error('发送消息失败，请重试');
    } finally {
      setIsLoading(false);
      setThinkingStep(null);
      // 重新加载会话列表
      loadSessions();
    }
  };

  return (
    <Layout className="chat-page">
      <Sider
        width={280}
        breakpoint="lg"
        collapsedWidth="0"
        className="chat-sider"
      >
        <SessionList
          sessions={sessions}
          currentSessionId={sessionId}
          onSelectSession={handleSelectSession}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
        />
      </Sider>

      <Drawer
        title="对话列表"
        placement="left"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={280}
      >
        <SessionList
          sessions={sessions}
          currentSessionId={sessionId}
          onSelectSession={handleSelectSession}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
        />
      </Drawer>

      <Layout>
        <Header className="chat-header">
          <div className="header-left">
            <Button
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setDrawerVisible(true)}
              className="menu-button"
            />
            <div>
              <h2>DeepResearch Agent</h2>
              <p>深度研究 AI 助手</p>
            </div>
          </div>
          <div className="header-right">
            <Switch
              checked={useMultiAgent}
              onChange={setUseMultiAgent}
              checkedChildren="多Agent"
              unCheckedChildren="单Agent"
            />
          </div>
        </Header>
      
        <Content className="chat-content">
          <div className="messages-container">
            {messages.length === 0 ? (
              <div className="empty-state">
                <h3>👋 你好！我是 DeepResearch Agent</h3>
                <p>我可以帮你深度研究任何话题，并生成详细的研究报告。</p>
                <p>请告诉我你想了解什么？</p>
                {useMultiAgent && (
                  <p className="mode-hint">💡 当前使用<strong>多Agent模式</strong>：将自动规划任务、收集信息并生成报告</p>
                )}
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <MessageItem key={message.id} message={message} />
                ))}
                {thinkingStep && (
                  <ThinkingIndicator
                    step={thinkingStep.step}
                    message={thinkingStep.message}
                  />
                )}
                {isLoading && !thinkingStep && (
                  <div className="loading-indicator">
                    <Spin tip="正在思考中..." />
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>
        </Content>

        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading}
          placeholder="请输入您想研究的话题..."
        />
      </Layout>
    </Layout>
  );
};

export default ChatPage;

