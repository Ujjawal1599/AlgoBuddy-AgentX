import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  BarChartOutlined,
  LineChartOutlined,
  WalletOutlined,
  ExperimentOutlined,
  SettingOutlined
} from '@ant-design/icons';

const { Sider } = Layout;

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/strategies',
      icon: <BarChartOutlined />,
      label: 'Strategies',
    },
    {
      key: '/trading',
      icon: <LineChartOutlined />,
      label: 'Trading',
    },
    {
      key: '/portfolio',
      icon: <WalletOutlined />,
      label: 'Portfolio',
    },
    {
      key: '/backtesting',
      icon: <ExperimentOutlined />,
      label: 'Backtesting',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  return (
    <Sider
      width={250}
      style={{
        background: '#001529',
      }}
    >
      <div style={{ 
        height: '64px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        borderBottom: '1px solid #303030'
      }}>
        <h2 style={{ color: '#fff', margin: 0 }}>TiDB Agentx</h2>
      </div>
      
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ 
          borderRight: 0,
          background: '#001529'
        }}
      />
    </Sider>
  );
};

export default Sidebar; 