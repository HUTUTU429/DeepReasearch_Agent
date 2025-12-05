/**
 * 会话列表组件
 */
import React from 'react';
import { List, Typography, Button, Popconfirm } from 'antd';
import { MessageOutlined, DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { Session } from '../types';
import './SessionList.css';

const { Text } = Typography;

interface SessionListProps {
  sessions: Session[];
  currentSessionId?: string;
  onSelectSession: (sessionId: string) => void;
  onCreateSession: () => void;
  onDeleteSession: (sessionId: string) => void;
}

const SessionList: React.FC<SessionListProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
}) => {
  return (
    <div className="session-list">
      <div className="session-list-header">
        <h3>对话列表</h3>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={onCreateSession}
          size="small"
        >
          新对话
        </Button>
      </div>

      <List
        className="sessions"
        dataSource={sessions}
        renderItem={(session) => (
          <List.Item
            className={`session-item ${session.session_id === currentSessionId ? 'active' : ''}`}
            onClick={() => onSelectSession(session.session_id)}
          >
            <div className="session-content">
              <div className="session-title">
                <MessageOutlined />
                <Text ellipsis>{session.title}</Text>
              </div>
              <div className="session-meta">
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {new Date(session.updated_at).toLocaleDateString('zh-CN')}
                </Text>
              </div>
            </div>
            <Popconfirm
              title="确定删除这个对话吗？"
              onConfirm={(e) => {
                e?.stopPropagation();
                onDeleteSession(session.session_id);
              }}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="text"
                danger
                size="small"
                icon={<DeleteOutlined />}
                onClick={(e) => e.stopPropagation()}
              />
            </Popconfirm>
          </List.Item>
        )}
      />
    </div>
  );
};

export default SessionList;

