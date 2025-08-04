# TiDB Agentx Hackathon - Algorithmic Trading with Agentic AI

A comprehensive algorithmic trading platform that uses agentic AI to develop, test, and optimize trading strategies using Zerodha APIs and TiDB for data storage.

## 🚀 Features

- **Agentic AI System**: Multi-agent architecture for strategy development and optimization
- **Real-time Trading**: Integration with Zerodha APIs for live market data
- **Strategy Backtesting**: Historical data analysis and performance evaluation
- **Risk Management**: Automated risk assessment and position sizing
- **Modern UI**: React-based dashboard for strategy monitoring
- **Scalable Backend**: FastAPI with TiDB integration

## 🏗️ Architecture

```
├── AI_service/          # Agentic AI modules
│   ├── agents/         # AI agents for strategy development
│   ├── strategies/     # Trading strategy implementations
│   └── backtesting/    # Backtesting engine
├── backend/            # FastAPI backend
│   ├── api/           # API endpoints
│   ├── models/        # Data models
│   └── services/      # Business logic
├── frontend/          # React frontend
│   ├── src/          # React components
│   └── public/       # Static assets
└── database/         # TiDB schemas and migrations
```

## 🤖 AI Agents

### StrategyGeneratorAgent
- Generates trading strategies based on technical indicators
- Outputs Python code for strategy logic
- Considers market conditions and risk parameters

### BacktestAgent
- Runs strategies on historical data
- Calculates performance metrics (Sharpe ratio, drawdown, etc.)
- Generates detailed performance reports

### EvaluatorAgent
- Analyzes backtest results
- Determines strategy viability
- Suggests improvements or accepts strategy

### RiskManagerAgent
- Monitors live trading positions
- Implements risk controls
- Manages position sizing and stop-losses

## 🛠️ Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- TiDB instance
- Zerodha API credentials

### Installation

1. **Clone and setup environment**
```bash
git clone <repository>
cd TiDB-Agentx-Hackathon
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **AI Service Setup**
```bash
cd AI_service
pip install -r requirements.txt
```

5. **Database Setup**
```bash
# Configure TiDB connection in backend/config/database.py
```

## 🚀 Running the Application

1. **Start Backend**
```bash
cd backend
uvicorn main:app --reload
```

2. **Start Frontend**
```bash
cd frontend
npm start
```

3. **Start AI Service**
```bash
cd AI_service
python main.py
```

## 📊 API Endpoints

- `POST /api/strategies/generate` - Generate new trading strategy
- `POST /api/strategies/backtest` - Run backtest on strategy
- `GET /api/strategies/{id}` - Get strategy details
- `POST /api/trading/execute` - Execute live trade
- `GET /api/portfolio/status` - Get portfolio status

## 🔧 Configuration

Create `.env` files in each service directory:

```env
# Backend .env
DATABASE_URL=mysql://user:password@localhost:4000/trading_db
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_secret
OPENAI_API_KEY=your_openai_key

# AI Service .env
OPENAI_API_KEY=your_openai_key
MODEL_NAME=gpt-4
```

## 📈 Usage

1. **Strategy Generation**: Use the AI agents to generate trading strategies
2. **Backtesting**: Test strategies on historical data
3. **Live Trading**: Deploy approved strategies for live trading
4. **Monitoring**: Monitor performance through the React dashboard

## 🤝 Contributing

This project is developed for the TiDB Agentx Hackathon. Contributions are welcome!

## 📄 License

MIT License 