import React from 'react';
import { Layout, Typography, Space, Badge, Avatar } from 'antd';
import { BellOutlined, UserOutlined, SettingOutlined } from '@ant-design/icons';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

const Header = () => {
  return (
    <AntHeader style={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between',
      background: '#fff',
      padding: '0 24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
    }}>
      <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
        TiDB Agentx Trading Platform
      </Title>
      
      <Space size="large">
        <Badge count={5}>
          <BellOutlined style={{ fontSize: '18px', color: '#666' }} />
        </Badge>
        
        <Space>
          <Avatar icon={<UserOutlined />} />
          <span style={{ color: '#666' }}>Trading User</span>
        </Space>
        
        <SettingOutlined style={{ fontSize: '18px', color: '#666' }} />
      </Space>
    </AntHeader>
  );
};

export default Header; 