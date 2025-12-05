/**
 * 消息项组件
 */
import React from 'react';
import { Card, Typography, Tag, Collapse } from 'antd';
import { UserOutlined, RobotOutlined, ToolOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { Message, StreamEvent, ToolCall, ToolResult } from '../types';
import './MessageItem.css';

const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.role === 'user';

  // 渲染工具调用
  const renderToolCall = (event: StreamEvent) => {
    const toolCall = event.content as ToolCall;
    return (
      <div className="tool-call">
        <Tag icon={<ToolOutlined />} color="blue">
          调用工具: {toolCall.tool}
        </Tag>
        <Paragraph>
          <Text type="secondary">输入参数:</Text>
          <pre>{JSON.stringify(toolCall.input, null, 2)}</pre>
        </Paragraph>
      </div>
    );
  };

  // 渲染工具结果
  const renderToolResult = (event: StreamEvent) => {
    const toolResult = event.content as ToolResult;
    return (
      <div className="tool-result">
        <Tag icon={<ToolOutlined />} color="green">
          工具结果: {toolResult.tool}
        </Tag>
        <Paragraph>
          <Text type="secondary">输出结果:</Text>
          <pre>{JSON.stringify(toolResult.output, null, 2)}</pre>
        </Paragraph>
      </div>
    );
  };

  // 渲染事件详情
  const renderEvents = () => {
    if (!message.events || message.events.length === 0) return null;

    const toolEvents = message.events.filter(
      e => e.type === 'tool_call' || e.type === 'tool_result'
    );

    if (toolEvents.length === 0) return null;

    return (
      <Collapse ghost className="message-events">
        <Panel header={`查看执行详情 (${toolEvents.length})`} key="1">
          {toolEvents.map((event, index) => (
            <div key={index} className="event-item">
              {event.type === 'tool_call' && renderToolCall(event)}
              {event.type === 'tool_result' && renderToolResult(event)}
            </div>
          ))}
        </Panel>
      </Collapse>
    );
  };

  return (
    <div className={`message-item ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-avatar">
        {isUser ? (
          <UserOutlined style={{ fontSize: '24px' }} />
        ) : (
          <RobotOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
        )}
      </div>
      <div className="message-content">
        <Card
          className="message-card"
          bordered={false}
          size="small"
        >
          <div className="message-text">
            {isUser ? (
              <Text>{message.content}</Text>
            ) : (
              <ReactMarkdown>{message.content}</ReactMarkdown>
            )}
          </div>
          {renderEvents()}
        </Card>
        <div className="message-time">
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {new Date(message.timestamp).toLocaleTimeString('zh-CN')}
          </Text>
        </div>
      </div>
    </div>
  );
};

export default MessageItem;

