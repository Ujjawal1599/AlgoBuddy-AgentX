# TiDB Agentx Trading Platform - Setup Guide

## 🚀 Quick Start

This guide will help you set up the complete TiDB Agentx Trading Platform with agentic AI for algorithmic trading.

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- TiDB instance (or MySQL compatible database)
- Zerodha API credentials (optional for demo)
- OpenAI API key

## 🛠️ Installation Steps

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd TiDB-Agentx-Hackathon

# Create virtual environments
python -m venv backend/venv
python -m venv AI_service/venv
```

### 2. Backend Setup

```bash
cd backend

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration
```

### 3. AI Service Setup

```bash
cd ../AI_service

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file (optional)
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

### 5. Database Setup

```bash
# Start TiDB (if using local instance)
# Or configure your existing TiDB/MySQL instance

# Update DATABASE_URL in backend/.env
DATABASE_URL=mysql://username:password@host:port/database_name
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=mysql://root:@localhost:4000/trading_db
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_secret
OPENAI_API_KEY=your_openai_api_key
AI_SERVICE_URL=http://localhost:8001
LOG_LEVEL=INFO
```

#### AI Service (.env)
```env
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4
AI_SERVICE_URL=http://localhost:8001
LOG_LEVEL=INFO
```

## 🚀 Running the Application

### 1. Start Backend Service

```bash
cd backend
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start AI Service

```bash
cd AI_service
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the AI service
python main.py
```

### 3. Start Frontend

```bash
cd frontend

# Start React development server
npm start
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **AI Service**: http://localhost:8001
- **API Documentation**: http://localhost:8000/docs

## 🤖 AI Agents Overview

### StrategyGeneratorAgent
- Generates trading strategies using OpenAI
- Supports multiple technical indicators (RSI, MACD, SMA, Bollinger Bands)
- Configurable risk levels and capital allocation

### BacktestAgent
- Runs strategies on historical data
- Calculates comprehensive performance metrics
- Generates detailed trade logs and equity curves

### EvaluatorAgent
- Analyzes backtest results
- Provides AI-powered recommendations
- Determines strategy viability for live trading

### RiskManagerAgent
- Monitors live trading positions
- Implements risk controls and position sizing
- Manages stop-loss and take-profit levels

## 📊 Features

### Dashboard
- Real-time portfolio overview
- Performance metrics and charts
- Recent trades and strategy status

### Strategies
- Create and manage trading strategies
- AI-powered strategy generation
- Performance tracking and optimization

### Trading
- Live trading interface
- Market data display
- Trade execution and monitoring

### Portfolio
- Portfolio allocation visualization
- Position tracking and P&L analysis
- Risk metrics and performance indicators

### Backtesting
- Historical strategy testing
- Performance analysis and visualization
- Trade-by-trade analysis

## 🔗 API Endpoints

### Strategies
- `POST /api/strategies/generate` - Generate new strategy
- `POST /api/strategies/backtest` - Run backtest
- `GET /api/strategies/` - List strategies
- `GET /api/strategies/{id}` - Get strategy details

### Trading
- `POST /api/trading/execute` - Execute trade
- `GET /api/trading/` - Get trade history
- `GET /api/trading/summary/statistics` - Trading statistics

### Portfolio
- `GET /api/portfolio/` - Portfolio overview
- `GET /api/portfolio/{id}/status` - Portfolio status
- `GET /api/portfolio/{id}/performance` - Performance metrics

### Zerodha Integration
- `GET /api/zerodha/market-data/{symbol}` - Market data
- `GET /api/zerodha/current-price/{symbol}` - Current price
- `POST /api/zerodha/place-order` - Place order

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Usage Examples

### 1. Generate a Trading Strategy

```python
import requests

# Generate RSI strategy for AAPL
response = requests.post("http://localhost:8000/api/strategies/generate", json={
    "symbol": "AAPL",
    "indicators": ["RSI", "MACD"],
    "timeframe": "1d",
    "risk_level": "medium",
    "capital": 100000
})

strategy_code = response.json()["strategy_code"]
```

### 2. Run Backtest

```python
# Run backtest on generated strategy
response = requests.post("http://localhost:8000/api/strategies/backtest", json={
    "strategy_code": strategy_code,
    "symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-12-01",
    "initial_capital": 100000
})

results = response.json()
```

### 3. Evaluate Strategy

```python
# Evaluate backtest results
response = requests.post("http://localhost:8000/api/strategies/evaluate", json=results)
evaluation = response.json()
```

## 🔒 Security Considerations

- Store API keys securely in environment variables
- Use HTTPS in production
- Implement proper authentication and authorization
- Regular security updates and monitoring

## 🚀 Deployment

### Production Setup

1. **Database**: Use production TiDB/MySQL instance
2. **Backend**: Deploy with Gunicorn or similar WSGI server
3. **Frontend**: Build and serve static files
4. **AI Service**: Deploy as separate microservice
5. **Load Balancer**: Configure for high availability

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 📝 Troubleshooting

### Common Issues

1. **Database Connection**: Check DATABASE_URL and network connectivity
2. **API Keys**: Verify OpenAI and Zerodha API keys are valid
3. **Port Conflicts**: Ensure ports 3000, 8000, 8001 are available
4. **Dependencies**: Update pip and npm packages if needed

### Logs

- Backend logs: Check console output or log files
- AI Service logs: Monitor for OpenAI API errors
- Frontend logs: Check browser console for errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Create an issue on GitHub

---

**Happy Trading! 🚀📈** 