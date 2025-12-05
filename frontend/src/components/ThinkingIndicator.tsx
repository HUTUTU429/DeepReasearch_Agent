/**
 * 思考过程指示器组件
 */
import React from 'react';
import { Card, Tag, Typography } from 'antd';
import { ThunderboltOutlined, SearchOutlined, EditOutlined } from '@ant-design/icons';
import './ThinkingIndicator.css';

const { Text } = Typography;

interface ThinkingIndicatorProps {
  step: 'planning' | 'researching' | 'writing';
  message: string;
  metadata?: Record<string, any>;
}

const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({
  step,
  message,
}) => {
  const getIcon = () => {
    switch (step) {
      case 'planning':
        return <ThunderboltOutlined />;
      case 'researching':
        return <SearchOutlined />;
      case 'writing':
        return <EditOutlined />;
      default:
        return <ThunderboltOutlined />;
    }
  };

  const getColor = () => {
    switch (step) {
      case 'planning':
        return 'blue';
      case 'researching':
        return 'green';
      case 'writing':
        return 'purple';
      default:
        return 'default';
    }
  };

  return (
    <Card className="thinking-indicator" size="small" bordered={false}>
      <div className="thinking-content">
        <Tag icon={getIcon()} color={getColor()}>
          {step === 'planning' && '规划中'}
          {step === 'researching' && '研究中'}
          {step === 'writing' && '撰写中'}
        </Tag>
        <Text className="thinking-message">{message}</Text>
      </div>
    </Card>
  );
};

export default ThinkingIndicator;

