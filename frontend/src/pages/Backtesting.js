import React, { useState } from 'react';
import { Card, Button, Form, Input, Select, InputNumber, Row, Col, Statistic, Progress, Table, Tag, message } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { PlayCircleOutlined, BarChartOutlined, ExperimentOutlined } from '@ant-design/icons';

const { Option } = Select;

const Backtesting = () => {
  const [form] = Form.useForm();
  const [backtestResults, setBacktestResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const [performanceData] = useState([
    { date: '2023-11-01', value: 100000 },
    { date: '2023-11-08', value: 102500 },
    { date: '2023-11-15', value: 101200 },
    { date: '2023-11-22', value: 104800 },
    { date: '2023-11-29', value: 107500 },
    { date: '2023-12-01', value: 112500 }
  ]);

  const [tradesData] = useState([
    { month: 'Jan', trades: 12, pnl: 2500 },
    { month: 'Feb', trades: 18, pnl: 3200 },
    { month: 'Mar', trades: 15, pnl: 1800 },
    { month: 'Apr', trades: 22, pnl: 4100 },
    { month: 'May', trades: 20, pnl: 3600 },
    { month: 'Jun', trades: 25, pnl: 4800 }
  ]);

  const handleBacktest = async (values) => {
    setIsRunning(true);
    
    // Simulate backtest processing
    setTimeout(() => {
      const results = {
        totalReturn: 12.5,
        sharpeRatio: 1.2,
        maxDrawdown: -5.2,
        winRate: 65.0,
        totalTrades: 25,
        profitFactor: 1.8,
        avgTrade: 125.50,
        bestTrade: 850.00,
        worstTrade: -320.00,
        avgWin: 280.00,
        avgLoss: -180.00,
        trades: [
          { date: '2023-11-01', action: 'BUY', symbol: 'AAPL', quantity: 100, price: 145.00, pnl: 525.00 },
          { date: '2023-11-05', action: 'SELL', symbol: 'AAPL', quantity: 100, price: 150.25, pnl: 525.00 },
          { date: '2023-11-08', action: 'BUY', symbol: 'GOOGL', quantity: 5, price: 2750.00, pnl: 252.50 },
          { date: '2023-11-12', action: 'SELL', symbol: 'GOOGL', quantity: 5, price: 2800.50, pnl: 252.50 }
        ]
      };
      
      setBacktestResults(results);
      setIsRunning(false);
      message.success('Backtest completed successfully!');
    }, 3000);
  };

  const tradeColumns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
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
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      render: (price) => `$${price.toFixed(2)}`,
    },
    {
      title: 'P&L',
      dataIndex: 'pnl',
      key: 'pnl',
      render: (pnl) => (
        <span style={{ color: pnl >= 0 ? '#52c41a' : '#ff4d4f' }}>
          {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
        </span>
      ),
    },
  ];

  return (
    <div>
      <h1>Strategy Backtesting</h1>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Backtest Configuration" className="backtest-results">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleBacktest}
            >
              <Form.Item
                name="strategy_name"
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
                name="start_date"
                label="Start Date"
                rules={[{ required: true, message: 'Please select start date' }]}
              >
                <Input type="date" />
              </Form.Item>

              <Form.Item
                name="end_date"
                label="End Date"
                rules={[{ required: true, message: 'Please select end date' }]}
              >
                <Input type="date" />
              </Form.Item>

              <Form.Item
                name="initial_capital"
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
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  icon={<PlayCircleOutlined />}
                  loading={isRunning}
                  style={{ width: '100%' }}
                >
                  {isRunning ? 'Running Backtest...' : 'Run Backtest'}
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Quick Stats">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic
                  title="Total Return"
                  value={backtestResults?.totalReturn || 0}
                  suffix="%"
                  valueStyle={{ color: '#3f8600' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Sharpe Ratio"
                  value={backtestResults?.sharpeRatio || 0}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Max Drawdown"
                  value={backtestResults?.maxDrawdown || 0}
                  suffix="%"
                  valueStyle={{ color: '#cf1322' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Win Rate"
                  value={backtestResults?.winRate || 0}
                  suffix="%"
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {backtestResults && (
        <>
          {/* Performance Metrics */}
          <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
            <Col span={24}>
              <Card title="Performance Metrics" className="backtest-results">
                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={12} lg={6}>
                    <div className="metric-card">
                      <div className="metric-value">{backtestResults.totalReturn}%</div>
                      <div className="metric-label">Total Return</div>
                    </div>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <div className="metric-card">
                      <div className="metric-value">{backtestResults.sharpeRatio}</div>
                      <div className="metric-label">Sharpe Ratio</div>
                    </div>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <div className="metric-card">
                      <div className="metric-value">{backtestResults.maxDrawdown}%</div>
                      <div className="metric-label">Max Drawdown</div>
                    </div>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <div className="metric-card">
                      <div className="metric-value">{backtestResults.winRate}%</div>
                      <div className="metric-label">Win Rate</div>
                    </div>
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>

          {/* Performance Chart */}
          <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
            <Col span={24}>
              <Card title="Equity Curve" className="backtest-results">
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

          {/* Monthly Performance */}
          <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
            <Col span={24}>
              <Card title="Monthly Performance" className="backtest-results">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={tradesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="pnl" fill="#52c41a" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          {/* Trades Table */}
          <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
            <Col span={24}>
              <Card title="Backtest Trades" className="backtest-results">
                <Table 
                  columns={tradeColumns} 
                  dataSource={backtestResults.trades} 
                  pagination={{ pageSize: 10 }}
                  size="small"
                />
              </Card>
            </Col>
          </Row>
        </>
      )}
    </div>
  );
};

export default Backtesting; 