import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Progress, Table, Tag } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUpOutlined, ArrowDownOutlined, DollarOutlined, RiseOutlined } from '@ant-design/icons';

const Dashboard = () => {
  const [portfolioData, setPortfolioData] = useState({
    totalValue: 125000,
    dailyChange: 2500,
    totalReturn: 25.0,
    activeStrategies: 3,
    totalTrades: 45
  });

  const [recentTrades, setRecentTrades] = useState([
    {
      key: '1',
      symbol: 'AAPL',
      action: 'BUY',
      quantity: 100,
      price: 150.25,
      timestamp: '2023-12-01 14:30:00',
      status: 'executed'
    },
    {
      key: '2',
      symbol: 'GOOGL',
      action: 'SELL',
      quantity: 5,
      price: 2800.50,
      timestamp: '2023-12-01 13:15:00',
      status: 'executed'
    },
    {
      key: '3',
      symbol: 'TSLA',
      action: 'BUY',
      quantity: 50,
      price: 250.75,
      timestamp: '2023-12-01 12:45:00',
      status: 'executed'
    }
  ]);

  const [performanceData] = useState([
    { date: '2023-11-25', value: 100000 },
    { date: '2023-11-26', value: 102000 },
    { date: '2023-11-27', value: 101500 },
    { date: '2023-11-28', value: 103500 },
    { date: '2023-11-29', value: 105000 },
    { date: '2023-11-30', value: 107500 },
    { date: '2023-12-01', value: 125000 }
  ]);

  const tradeColumns = [
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: 'Action',
      dataIndex: 'action',
      key: 'action',
      render: (action) => (
        <Tag color={action === 'BUY' ? 'green' : 'red'}>
          {action}
        </Tag>
      ),
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      render: (price) => `$${price.toFixed(2)}`,
    },
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'executed' ? 'blue' : 'orange'}>
          {status}
        </Tag>
      ),
    },
  ];

  return (
    <div>
      <h1>Dashboard</h1>
      
      {/* Portfolio Overview */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Portfolio Value"
              value={portfolioData.totalValue}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Daily Change"
              value={portfolioData.dailyChange}
              prefix={<DollarOutlined />}
              valueStyle={{ color: portfolioData.dailyChange >= 0 ? '#3f8600' : '#cf1322' }}
              prefix={portfolioData.dailyChange >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Return"
              value={portfolioData.totalReturn}
              suffix="%"
              valueStyle={{ color: '#3f8600' }}
              prefix={<RiseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Strategies"
              value={portfolioData.activeStrategies}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Performance Chart */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="Portfolio Performance" className="dashboard-card">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#1890ff" 
                  strokeWidth={2}
                  dot={{ fill: '#1890ff', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Recent Trades */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="Recent Trades" className="dashboard-card">
            <Table 
              columns={tradeColumns} 
              dataSource={recentTrades} 
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      {/* Strategy Performance */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="Strategy Performance" className="dashboard-card">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} lg={8}>
                <Card size="small" title="RSI Strategy">
                  <Statistic
                    title="Return"
                    value={12.5}
                    suffix="%"
                    valueStyle={{ color: '#3f8600' }}
                  />
                  <Progress percent={75} status="active" />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={8}>
                <Card size="small" title="MACD Strategy">
                  <Statistic
                    title="Return"
                    value={8.3}
                    suffix="%"
                    valueStyle={{ color: '#3f8600' }}
                  />
                  <Progress percent={60} status="active" />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={8}>
                <Card size="small" title="Bollinger Bands">
                  <Statistic
                    title="Return"
                    value={15.2}
                    suffix="%"
                    valueStyle={{ color: '#3f8600' }}
                  />
                  <Progress percent={85} status="active" />
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 