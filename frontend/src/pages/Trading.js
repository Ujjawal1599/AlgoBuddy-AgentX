import React, { useState } from 'react';
import { Card, Button, Form, Input, Select, InputNumber, Table, Tag, Space, message, Row, Col, Statistic } from 'antd';
import { SendOutlined, DollarOutlined, RiseOutlined, FallOutlined } from '@ant-design/icons';

const { Option } = Select;

const Trading = () => {
  const [form] = Form.useForm();
  const [trades, setTrades] = useState([
    {
      key: '1',
      symbol: 'AAPL',
      action: 'BUY',
      quantity: 100,
      price: 150.25,
      value: 15025.00,
      status: 'executed',
      timestamp: '2023-12-01 14:30:00'
    },
    {
      key: '2',
      symbol: 'GOOGL',
      action: 'SELL',
      quantity: 5,
      price: 2800.50,
      value: 14002.50,
      status: 'executed',
      timestamp: '2023-12-01 13:15:00'
    }
  ]);

  const [marketData] = useState({
    AAPL: { price: 150.25, change: 2.50, changePercent: 1.69 },
    GOOGL: { price: 2800.50, change: 15.00, changePercent: 0.54 },
    TSLA: { price: 250.75, change: -10.25, changePercent: -3.93 },
    MSFT: { price: 300.00, change: 5.00, changePercent: 1.69 }
  });

  const columns = [
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
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      render: (value) => `$${value.toFixed(2)}`,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'executed' ? 'blue' : 'orange'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
    },
  ];

  const handleTrade = async (values) => {
    const newTrade = {
      key: (trades.length + 1).toString(),
      symbol: values.symbol,
      action: values.action,
      quantity: values.quantity,
      price: marketData[values.symbol]?.price || 100.00,
      value: values.quantity * (marketData[values.symbol]?.price || 100.00),
      status: 'executed',
      timestamp: new Date().toLocaleString()
    };

    setTrades(prev => [newTrade, ...prev]);
    form.resetFields();
    message.success(`Trade executed: ${values.action} ${values.quantity} ${values.symbol}`);
  };

  return (
    <div>
      <h1>Live Trading</h1>
      
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Portfolio Value"
              value={125000}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Available Cash"
              value={45000}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Today's P&L"
              value={2500}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Open Positions"
              value={3}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Execute Trade" className="trading-panel">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleTrade}
            >
              <Form.Item
                name="symbol"
                label="Symbol"
                rules={[{ required: true, message: 'Please select symbol' }]}
              >
                <Select placeholder="Select symbol">
                  <Option value="AAPL">AAPL - Apple Inc.</Option>
                  <Option value="GOOGL">GOOGL - Alphabet Inc.</Option>
                  <Option value="MSFT">MSFT - Microsoft Corporation</Option>
                  <Option value="TSLA">TSLA - Tesla Inc.</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="action"
                label="Action"
                rules={[{ required: true, message: 'Please select action' }]}
              >
                <Select placeholder="Select action">
                  <Option value="BUY">BUY</Option>
                  <Option value="SELL">SELL</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="quantity"
                label="Quantity"
                rules={[{ required: true, message: 'Please enter quantity' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="Enter quantity"
                  min={1}
                />
              </Form.Item>

              <Form.Item
                name="order_type"
                label="Order Type"
                initialValue="MARKET"
              >
                <Select>
                  <Option value="MARKET">Market</Option>
                  <Option value="LIMIT">Limit</Option>
                  <Option value="STOP">Stop</Option>
                </Select>
              </Form.Item>

              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  icon={<SendOutlined />}
                  style={{ width: '100%' }}
                >
                  Execute Trade
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Market Data" className="trading-panel">
            {Object.entries(marketData).map(([symbol, data]) => (
              <div key={symbol} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '8px 0',
                borderBottom: '1px solid #f0f0f0'
              }}>
                <div>
                  <strong>{symbol}</strong>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    ${data.price.toFixed(2)}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ 
                    color: data.change >= 0 ? '#52c41a' : '#ff4d4f',
                    fontWeight: 'bold'
                  }}>
                    {data.change >= 0 ? '+' : ''}{data.change.toFixed(2)}
                  </div>
                  <div style={{ 
                    fontSize: '12px',
                    color: data.change >= 0 ? '#52c41a' : '#ff4d4f'
                  }}>
                    {data.change >= 0 ? '+' : ''}{data.changePercent.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </Card>
        </Col>
      </Row>

      <Card title="Recent Trades" style={{ marginTop: 16 }}>
        <Table 
          columns={columns} 
          dataSource={trades} 
          pagination={{ pageSize: 10 }}
          size="small"
        />
      </Card>
    </div>
  );
};

export default Trading; 