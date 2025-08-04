import React, { useState } from 'react';
import { Card, Button, Table, Tag, Space, Modal, Form, Input, Select, InputNumber, message } from 'antd';
import { PlusOutlined, PlayCircleOutlined, PauseCircleOutlined, DeleteOutlined } from '@ant-design/icons';

const { Option } = Select;

const Strategies = () => {
  const [strategies, setStrategies] = useState([
    {
      id: 1,
      name: 'RSI Strategy',
      symbol: 'AAPL',
      status: 'active',
      totalReturn: 12.5,
      sharpeRatio: 1.2,
      maxDrawdown: -5.2,
      winRate: 65.0,
      totalTrades: 25,
      created_at: '2023-11-15'
    },
    {
      id: 2,
      name: 'MACD Strategy',
      symbol: 'GOOGL',
      status: 'active',
      totalReturn: 8.3,
      sharpeRatio: 0.8,
      maxDrawdown: -8.1,
      winRate: 58.0,
      totalTrades: 18,
      created_at: '2023-11-20'
    },
    {
      id: 3,
      name: 'Bollinger Bands',
      symbol: 'TSLA',
      status: 'inactive',
      totalReturn: 15.2,
      sharpeRatio: 1.5,
      maxDrawdown: -3.8,
      winRate: 72.0,
      totalTrades: 32,
      created_at: '2023-11-25'
    }
  ]);

  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : 'orange'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Total Return',
      dataIndex: 'totalReturn',
      key: 'totalReturn',
      render: (value) => `${value}%`,
    },
    {
      title: 'Sharpe Ratio',
      dataIndex: 'sharpeRatio',
      key: 'sharpeRatio',
    },
    {
      title: 'Max Drawdown',
      dataIndex: 'maxDrawdown',
      key: 'maxDrawdown',
      render: (value) => `${value}%`,
    },
    {
      title: 'Win Rate',
      dataIndex: 'winRate',
      key: 'winRate',
      render: (value) => `${value}%`,
    },
    {
      title: 'Total Trades',
      dataIndex: 'totalTrades',
      key: 'totalTrades',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            icon={record.status === 'active' ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            size="small"
            onClick={() => toggleStrategy(record.id)}
          >
            {record.status === 'active' ? 'Pause' : 'Activate'}
          </Button>
          <Button
            type="default"
            icon={<DeleteOutlined />}
            size="small"
            danger
            onClick={() => deleteStrategy(record.id)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  const toggleStrategy = (id) => {
    setStrategies(prev => 
      prev.map(strategy => 
        strategy.id === id 
          ? { ...strategy, status: strategy.status === 'active' ? 'inactive' : 'active' }
          : strategy
      )
    );
    message.success('Strategy status updated');
  };

  const deleteStrategy = (id) => {
    setStrategies(prev => prev.filter(strategy => strategy.id !== id));
    message.success('Strategy deleted');
  };

  const handleCreateStrategy = async (values) => {
    const newStrategy = {
      id: strategies.length + 1,
      name: values.name,
      symbol: values.symbol,
      status: 'draft',
      totalReturn: 0,
      sharpeRatio: 0,
      maxDrawdown: 0,
      winRate: 0,
      totalTrades: 0,
      created_at: new Date().toISOString().split('T')[0]
    };
    
    setStrategies(prev => [...prev, newStrategy]);
    setIsModalVisible(false);
    form.resetFields();
    message.success('Strategy created successfully');
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1>Strategies</h1>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => setIsModalVisible(true)}
        >
          Create Strategy
        </Button>
      </div>

      <Card>
        <Table 
          columns={columns} 
          dataSource={strategies} 
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="Create New Strategy"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateStrategy}
        >
          <Form.Item
            name="name"
            label="Strategy Name"
            rules={[{ required: true, message: 'Please enter strategy name' }]}
          >
            <Input placeholder="Enter strategy name" />
          </Form.Item>

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
              <Option value="AMZN">AMZN - Amazon.com Inc.</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="indicators"
            label="Technical Indicators"
            rules={[{ required: true, message: 'Please select indicators' }]}
          >
            <Select mode="multiple" placeholder="Select indicators">
              <Option value="RSI">RSI</Option>
              <Option value="MACD">MACD</Option>
              <Option value="SMA">Simple Moving Average</Option>
              <Option value="BB">Bollinger Bands</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="timeframe"
            label="Timeframe"
            rules={[{ required: true, message: 'Please select timeframe' }]}
          >
            <Select placeholder="Select timeframe">
              <Option value="1m">1 Minute</Option>
              <Option value="5m">5 Minutes</Option>
              <Option value="15m">15 Minutes</Option>
              <Option value="1h">1 Hour</Option>
              <Option value="1d">1 Day</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="risk_level"
            label="Risk Level"
            rules={[{ required: true, message: 'Please select risk level' }]}
          >
            <Select placeholder="Select risk level">
              <Option value="low">Low</Option>
              <Option value="medium">Medium</Option>
              <Option value="high">High</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="capital"
            label="Initial Capital"
            rules={[{ required: true, message: 'Please enter initial capital' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="Enter initial capital"
              min={1000}
              formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value.replace(/\$\s?|(,*)/g, '')}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Create Strategy
              </Button>
              <Button onClick={() => setIsModalVisible(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Strategies; 