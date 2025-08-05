import os
from typing import Dict, Any, List
import asyncio

# Try to import OpenAI, but don't fail if not available
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class EvaluatorAgent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Only initialize OpenAI client if API key is available
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.client = AsyncOpenAI(api_key=self.openai_api_key)
                self.use_openai = True
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                self.use_openai = False
        else:
            self.use_openai = False
            print("Warning: OpenAI API key not found. Using fallback evaluation.")
        
        # Define evaluation criteria
        self.criteria = {
            "min_total_return": 5.0,  # Minimum 5% return
            "min_sharpe_ratio": 0.5,  # Minimum Sharpe ratio
            "max_drawdown": -20.0,     # Maximum 20% drawdown
            "min_win_rate": 40.0,      # Minimum 40% win rate
            "min_trades": 5            # Minimum 5 trades
        }
    
    async def evaluate_strategy(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate strategy performance and provide recommendations
        """
        try:
            # Extract performance metrics
            metrics = backtest_results.get("performance_metrics", {})
            
            # Basic validation
            if "error" in metrics:
                return {
                    "status": "failed",
                    "reason": "Invalid backtest results",
                    "recommendation": "Re-run backtest with valid data"
                }
            
            # Calculate evaluation score
            evaluation_score = self._calculate_evaluation_score(metrics)
            
            # Determine strategy viability
            viability = self._determine_viability(metrics, evaluation_score)
            
            # Generate AI recommendations
            ai_recommendations = await self._generate_ai_recommendations(
                backtest_results, metrics, evaluation_score
            )
            
            return {
                "status": "success",
                "evaluation_score": evaluation_score,
                "viability": viability,
                "metrics_analysis": self._analyze_metrics(metrics),
                "recommendations": ai_recommendations,
                "decision": self._make_decision(viability, evaluation_score)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "recommendation": "Review strategy and re-evaluate"
            }
    
    def _calculate_evaluation_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate a composite evaluation score (0-100)"""
        
        score = 0
        max_score = 100
        
        # Total Return (30 points)
        total_return = metrics.get('total_return', 0)
        if total_return >= 20:
            score += 30
        elif total_return >= 10:
            score += 20
        elif total_return >= 5:
            score += 15
        elif total_return >= 0:
            score += 10
        else:
            score += max(0, 10 + total_return)  # Negative points for losses
        
        # Sharpe Ratio (25 points)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        if sharpe_ratio >= 1.5:
            score += 25
        elif sharpe_ratio >= 1.0:
            score += 20
        elif sharpe_ratio >= 0.5:
            score += 15
        elif sharpe_ratio >= 0:
            score += 10
        else:
            score += max(0, 5 + sharpe_ratio * 10)
        
        # Maximum Drawdown (20 points)
        max_drawdown = metrics.get('max_drawdown', 0)
        if max_drawdown >= -5:
            score += 20
        elif max_drawdown >= -10:
            score += 15
        elif max_drawdown >= -15:
            score += 10
        elif max_drawdown >= -20:
            score += 5
        else:
            score += max(0, 5 + max_drawdown / 4)
        
        # Win Rate (15 points)
        win_rate = metrics.get('win_rate', 0)
        if win_rate >= 70:
            score += 15
        elif win_rate >= 60:
            score += 12
        elif win_rate >= 50:
            score += 10
        elif win_rate >= 40:
            score += 8
        else:
            score += max(0, win_rate / 5)
        
        # Number of Trades (10 points)
        total_trades = metrics.get('total_trades', 0)
        if total_trades >= 20:
            score += 10
        elif total_trades >= 15:
            score += 8
        elif total_trades >= 10:
            score += 6
        elif total_trades >= 5:
            score += 4
        else:
            score += max(0, total_trades / 2)
        
        return min(max_score, max(0, score))
    
    def _determine_viability(self, metrics: Dict[str, Any], score: float) -> str:
        """Determine if the strategy is viable for live trading"""
        
        # Check minimum criteria
        total_return = metrics.get('total_return', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        max_drawdown = metrics.get('max_drawdown', 0)
        win_rate = metrics.get('win_rate', 0)
        total_trades = metrics.get('total_trades', 0)
        
        # Critical failures
        if total_return < self.criteria["min_total_return"]:
            return "REJECTED - Insufficient returns"
        
        if sharpe_ratio < self.criteria["min_sharpe_ratio"]:
            return "REJECTED - Poor risk-adjusted returns"
        
        if max_drawdown < self.criteria["max_drawdown"]:
            return "REJECTED - Excessive drawdown"
        
        if win_rate < self.criteria["min_win_rate"]:
            return "REJECTED - Low win rate"
        
        if total_trades < self.criteria["min_trades"]:
            return "REJECTED - Insufficient trading activity"
        
        # Score-based evaluation
        if score >= 80:
            return "APPROVED - Excellent performance"
        elif score >= 70:
            return "APPROVED - Good performance"
        elif score >= 60:
            return "CONDITIONAL - Acceptable with improvements"
        else:
            return "REJECTED - Poor overall performance"
    
    def _analyze_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual metrics and provide insights"""
        
        analysis = {}
        
        # Total Return Analysis
        total_return = metrics.get('total_return', 0)
        if total_return >= 20:
            analysis['return_rating'] = "Excellent"
        elif total_return >= 10:
            analysis['return_rating'] = "Good"
        elif total_return >= 5:
            analysis['return_rating'] = "Acceptable"
        else:
            analysis['return_rating'] = "Poor"
        
        # Sharpe Ratio Analysis
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        if sharpe_ratio >= 1.5:
            analysis['risk_rating'] = "Excellent"
        elif sharpe_ratio >= 1.0:
            analysis['risk_rating'] = "Good"
        elif sharpe_ratio >= 0.5:
            analysis['risk_rating'] = "Acceptable"
        else:
            analysis['risk_rating'] = "Poor"
        
        # Drawdown Analysis
        max_drawdown = metrics.get('max_drawdown', 0)
        if max_drawdown >= -5:
            analysis['drawdown_rating'] = "Excellent"
        elif max_drawdown >= -10:
            analysis['drawdown_rating'] = "Good"
        elif max_drawdown >= -15:
            analysis['drawdown_rating'] = "Acceptable"
        else:
            analysis['drawdown_rating'] = "Poor"
        
        # Win Rate Analysis
        win_rate = metrics.get('win_rate', 0)
        if win_rate >= 70:
            analysis['win_rate_rating'] = "Excellent"
        elif win_rate >= 60:
            analysis['win_rate_rating'] = "Good"
        elif win_rate >= 50:
            analysis['win_rate_rating'] = "Acceptable"
        else:
            analysis['win_rate_rating'] = "Poor"
        
        return analysis
    
    async def _generate_ai_recommendations(
        self,
        backtest_results: Dict[str, Any],
        metrics: Dict[str, Any],
        score: float
    ) -> Dict[str, Any]:
        """Generate AI-powered recommendations for strategy improvement"""
        
        if not self.use_openai:
            return {
                "ai_analysis": "AI recommendations not available - using fallback analysis",
                "key_insights": self._extract_key_insights(metrics),
                "improvement_areas": self._identify_improvement_areas(metrics)
            }
        
        try:
            # Create prompt for AI analysis
            prompt = f"""
            Analyze this trading strategy backtest results and provide specific recommendations:
            
            Performance Metrics:
            - Total Return: {metrics.get('total_return', 0):.2f}%
            - Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}
            - Maximum Drawdown: {metrics.get('max_drawdown', 0):.2f}%
            - Win Rate: {metrics.get('win_rate', 0):.2f}%
            - Total Trades: {metrics.get('total_trades', 0)}
            - Evaluation Score: {score:.1f}/100
            
            Symbol: {backtest_results.get('symbol', 'Unknown')}
            Period: {backtest_results.get('start_date', 'Unknown')} to {backtest_results.get('end_date', 'Unknown')}
            
            Provide specific recommendations for:
            1. Strategy improvements
            2. Risk management adjustments
            3. Parameter optimization
            4. Whether to proceed with live trading
            5. Alternative approaches to consider
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert algorithmic trading analyst. Provide specific, actionable recommendations for strategy improvement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_analysis = response.choices[0].message.content
            
            return {
                "ai_analysis": ai_analysis,
                "key_insights": self._extract_key_insights(metrics),
                "improvement_areas": self._identify_improvement_areas(metrics)
            }
            
        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
            return {
                "ai_analysis": "Unable to generate AI recommendations - using fallback analysis",
                "error": str(e),
                "key_insights": self._extract_key_insights(metrics),
                "improvement_areas": self._identify_improvement_areas(metrics)
            }
    
    def _extract_key_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Extract key insights from the metrics"""
        insights = []
        
        total_return = metrics.get('total_return', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        max_drawdown = metrics.get('max_drawdown', 0)
        win_rate = metrics.get('win_rate', 0)
        
        if total_return > 15:
            insights.append("High returns suggest strong strategy performance")
        elif total_return < 5:
            insights.append("Low returns indicate need for strategy optimization")
        
        if sharpe_ratio > 1.0:
            insights.append("Good risk-adjusted returns")
        elif sharpe_ratio < 0.5:
            insights.append("Poor risk-adjusted returns - consider risk management")
        
        if max_drawdown < -15:
            insights.append("High drawdown indicates need for better risk controls")
        
        if win_rate > 60:
            insights.append("Good win rate suggests reliable signal generation")
        elif win_rate < 40:
            insights.append("Low win rate indicates need for signal improvement")
        
        return insights
    
    def _identify_improvement_areas(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify specific areas for improvement"""
        improvements = []
        
        total_return = metrics.get('total_return', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        max_drawdown = metrics.get('max_drawdown', 0)
        win_rate = metrics.get('win_rate', 0)
        
        if total_return < 10:
            improvements.append("Optimize entry/exit timing")
            improvements.append("Consider additional technical indicators")
        
        if sharpe_ratio < 0.8:
            improvements.append("Implement better risk management")
            improvements.append("Reduce position sizing volatility")
        
        if max_drawdown < -10:
            improvements.append("Add stop-loss mechanisms")
            improvements.append("Implement position sizing rules")
        
        if win_rate < 50:
            improvements.append("Refine signal generation logic")
            improvements.append("Add confirmation indicators")
        
        return improvements
    
    def _make_decision(self, viability: str, score: float) -> str:
        """Make final decision on strategy deployment"""
        
        if "APPROVED" in viability:
            if score >= 80:
                return "DEPLOY - Strategy ready for live trading"
            else:
                return "DEPLOY WITH MONITORING - Deploy but closely monitor performance"
        elif "CONDITIONAL" in viability:
            return "ITERATE - Improve strategy before deployment"
        else:
            return "REJECT - Strategy needs significant improvements" 