import React, { useState } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Progress, PieChart, Pie, Cell, ResponsiveContainer } from 'antd';
import { DollarOutlined, RiseOutlined, FallOutlined, WalletOutlined } from '@ant-design/icons';

const Portfolio = () => {
  const [portfolioData] = useState({
    totalValue: 125000,
    cash: 45000,
    totalReturn: 25.0,
    dailyPnL: 2500,
    maxDrawdown: -8.5
  });

  const [positions] = useState([
    {
      key: '1',
      symbol: 'AAPL',
      quantity: 100,
      avgPrice: 145.00,
      currentPrice: 150.25,
      positionValue: 15025.00,
      unrealizedPnL: 525.00,
      unrealizedPnLPct: 3.62,
      returnPct: 3.62
    },
    {
      key: '2',
      symbol: 'GOOGL',
      quantity: 5,
      avgPrice: 2750.00,
      currentPrice: 2800.50,
      positionValue: 14002.50,
      unrealizedPnL: 252.50,
      unrealizedPnLPct: 1.84,
      returnPct: 1.84
    },
    {
      key: '3',
      symbol: 'TSLA',
      quantity: 50,
      avgPrice: 260.00,
      currentPrice: 250.75,
      positionValue: 12537.50,
      unrealizedPnL: -462.50,
      unrealizedPnLPct: -3.56,
      returnPct: -3.56
    }
  ]);

  const [allocationData] = useState([
    { name: 'Cash', value: 45000, color: '#1890ff' },
    { name: 'AAPL', value: 15025, color: '#52c41a' },
    { name: 'GOOGL', value: 14002.5, color: '#faad14' },
    { name: 'TSLA', value: 12537.5, color: '#ff4d4f' }
  ]);

  const columns = [
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: 'Avg Price',
      dataIndex: 'avgPrice',
      key: 'avgPrice',
      render: (price) => `$${price.toFixed(2)}`,
    },
    {
      title: 'Current Price',
      dataIndex: 'currentPrice',
      key: 'currentPrice',
      render: (price) => `$${price.toFixed(2)}`,
    },
    {
      title: 'Position Value',
      dataIndex: 'positionValue',
      key: 'positionValue',
      render: (value) => `$${value.toFixed(2)}`,
    },
    {
      title: 'Unrealized P&L',
      dataIndex: 'unrealizedPnL',
      key: 'unrealizedPnL',
      render: (pnl) => (
        <span style={{ color: pnl >= 0 ? '#52c41a' : '#ff4d4f' }}>
          {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
        </span>
      ),
    },
    {
      title: 'Return %',
      dataIndex: 'returnPct',
      key: 'returnPct',
      render: (pct) => (
        <span style={{ color: pct >= 0 ? '#52c41a' : '#ff4d4f' }}>
          {pct >= 0 ? '+' : ''}{pct.toFixed(2)}%
        </span>
      ),
    },
  ];

  const totalUnrealizedPnL = positions.reduce((sum, pos) => sum + pos.unrealizedPnL, 0);
  const totalPositionsValue = positions.reduce((sum, pos) => sum + pos.positionValue, 0);

  return (
    <div>
      <h1>Portfolio</h1>
      
      {/* Portfolio Overview */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Portfolio Value"
              value={portfolioData.totalValue}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Available Cash"
              value={portfolioData.cash}
              prefix={<WalletOutlined />}
              valueStyle={{ color: '#1890ff' }}
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
              title="Today's P&L"
              value={portfolioData.dailyPnL}
              prefix={<DollarOutlined />}
              valueStyle={{ color: portfolioData.dailyPnL >= 0 ? '#3f8600' : '#cf1322' }}
              prefix={portfolioData.dailyPnL >= 0 ? <RiseOutlined /> : <FallOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Unrealized P&L"
              value={totalUnrealizedPnL}
              prefix={<DollarOutlined />}
              valueStyle={{ color: totalUnrealizedPnL >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Positions Value"
              value={totalPositionsValue}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Max Drawdown"
              value={portfolioData.maxDrawdown}
              suffix="%"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Cash Allocation"
              value={((portfolioData.cash / portfolioData.totalValue) * 100).toFixed(1)}
              suffix="%"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Portfolio Allocation Chart */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Portfolio Allocation">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Performance Metrics">
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span>Total Return</span>
                <span style={{ color: '#3f8600' }}>+{portfolioData.totalReturn}%</span>
              </div>
              <Progress percent={portfolioData.totalReturn} strokeColor="#3f8600" />
            </div>
            
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span>Risk Level</span>
                <span style={{ color: '#faad14' }}>Medium</span>
              </div>
              <Progress percent={60} strokeColor="#faad14" />
            </div>
            
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span>Diversification</span>
                <span style={{ color: '#1890ff' }}>Good</span>
              </div>
              <Progress percent={75} strokeColor="#1890ff" />
            </div>
          </Card>
        </Col>
      </Row>

      {/* Positions Table */}
      <Card title="Current Positions">
        <Table 
          columns={columns} 
          dataSource={positions} 
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  );
};

export default Portfolio; 