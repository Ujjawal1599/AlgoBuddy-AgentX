import asyncio
import logging
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

# Try to import transformers for advanced sentiment analysis
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Try to import textblob for basic sentiment analysis
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# Try to import vaderSentiment for financial sentiment
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

logger = logging.getLogger(__name__)

class SentimentAnalyzerService:
    def __init__(self):
        self.analyzer = None
        self.financial_keywords = self._load_financial_keywords()
        
        # Initialize sentiment analyzers
        if TRANSFORMERS_AVAILABLE:
            try:
                self.transformer_pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
                self.use_transformers = True
                logger.info("Initialized transformer-based sentiment analyzer")
            except Exception as e:
                logger.warning(f"Failed to initialize transformers: {e}")
                self.use_transformers = False
        else:
            self.use_transformers = False
        
        if VADER_AVAILABLE:
            self.vader_analyzer = SentimentIntensityAnalyzer()
            self.use_vader = True
            logger.info("Initialized VADER sentiment analyzer")
        else:
            self.use_vader = False
        
        if TEXTBLOB_AVAILABLE:
            self.use_textblob = True
            logger.info("Initialized TextBlob sentiment analyzer")
        else:
            self.use_textblob = False
    
    def _load_financial_keywords(self) -> Dict[str, List[str]]:
        """Load financial sentiment keywords"""
        return {
            'positive': [
                'bullish', 'surge', 'rally', 'gain', 'profit', 'earnings', 'growth',
                'strong', 'beat', 'exceed', 'outperform', 'upgrade', 'buy', 'positive',
                'optimistic', 'recovery', 'breakthrough', 'milestone', 'record',
                'expansion', 'acquisition', 'merger', 'partnership', 'deal',
                'dividend', 'buyback', 'split', 'bonus', 'rights'
            ],
            'negative': [
                'bearish', 'crash', 'plunge', 'fall', 'loss', 'decline', 'drop',
                'weak', 'miss', 'disappoint', 'underperform', 'downgrade', 'sell',
                'negative', 'pessimistic', 'recession', 'crisis', 'bankruptcy',
                'default', 'debt', 'cut', 'layoff', 'closure', 'warning',
                'investigation', 'lawsuit', 'fine', 'penalty', 'scandal'
            ],
            'neutral': [
                'stable', 'maintain', 'hold', 'unchanged', 'flat', 'consolidate',
                'range', 'sideways', 'volatile', 'uncertain', 'mixed', 'neutral'
            ]
        }
    
    async def analyze_sentiment(self, text: str, context: str = "general") -> Dict[str, Any]:
        """
        Analyze sentiment of text with multiple methods
        """
        if not text or not text.strip():
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'confidence_score': 0.0,
                'financial_sentiment': 'neutral',
                'methods_used': []
            }
        
        results = {}
        methods_used = []
        
        # Clean and preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Financial keyword analysis
        financial_sentiment = self._analyze_financial_keywords(cleaned_text)
        results['financial_sentiment'] = financial_sentiment
        methods_used.append('financial_keywords')
        
        # VADER sentiment analysis (good for social media/financial text)
        if self.use_vader:
            vader_result = self._analyze_vader(cleaned_text)
            results['vader'] = vader_result
            methods_used.append('vader')
        
        # TextBlob sentiment analysis
        if self.use_textblob:
            textblob_result = self._analyze_textblob(cleaned_text)
            results['textblob'] = textblob_result
            methods_used.append('textblob')
        
        # Transformer-based analysis
        if self.use_transformers:
            transformer_result = await self._analyze_transformer(cleaned_text)
            results['transformer'] = transformer_result
            methods_used.append('transformer')
        
        # Combine results
        final_sentiment = self._combine_sentiment_results(results, methods_used)
        final_sentiment['methods_used'] = methods_used
        
        return final_sentiment
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for sentiment analysis"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        return text
    
    def _analyze_financial_keywords(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using financial keywords"""
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        words = text.split()
        
        for word in words:
            if word in self.financial_keywords['positive']:
                positive_count += 1
            elif word in self.financial_keywords['negative']:
                negative_count += 1
            elif word in self.financial_keywords['neutral']:
                neutral_count += 1
        
        total_keywords = positive_count + negative_count + neutral_count
        
        if total_keywords == 0:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
        
        # Calculate sentiment score
        score = (positive_count - negative_count) / total_keywords
        
        # Determine label
        if score > 0.1:
            label = 'positive'
        elif score < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Calculate confidence based on keyword density
        confidence = min(total_keywords / len(words), 1.0) if words else 0.0
        
        return {
            'score': score,
            'label': label,
            'confidence': confidence,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count
        }
    
    def _analyze_vader(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER"""
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            
            # VADER returns compound score (-1 to 1)
            compound_score = scores['compound']
            
            # Convert to our format
            if compound_score >= 0.05:
                label = 'positive'
            elif compound_score <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'score': compound_score,
                'label': label,
                'confidence': abs(compound_score),
                'raw_scores': scores
            }
        except Exception as e:
            logger.error(f"VADER analysis error: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
    
    def _analyze_textblob(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Convert to our format
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'score': polarity,
                'label': label,
                'confidence': abs(polarity) * (1 - subjectivity),  # Lower confidence for subjective text
                'subjectivity': subjectivity
            }
        except Exception as e:
            logger.error(f"TextBlob analysis error: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
    
    async def _analyze_transformer(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using transformer model"""
        try:
            # Truncate text if too long
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
            
            results = self.transformer_pipeline(text)
            
            # Find the highest scoring sentiment
            best_result = max(results[0], key=lambda x: x['score'])
            
            # Map labels to our format
            label_mapping = {
                'LABEL_0': 'negative',
                'LABEL_1': 'neutral', 
                'LABEL_2': 'positive'
            }
            
            mapped_label = label_mapping.get(best_result['label'], 'neutral')
            
            # Convert score to -1 to 1 range
            if mapped_label == 'positive':
                score = best_result['score']
            elif mapped_label == 'negative':
                score = -best_result['score']
            else:
                score = 0.0
            
            return {
                'score': score,
                'label': mapped_label,
                'confidence': best_result['score'],
                'raw_results': results
            }
        except Exception as e:
            logger.error(f"Transformer analysis error: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
    
    def _combine_sentiment_results(self, results: Dict[str, Any], methods_used: List[str]) -> Dict[str, Any]:
        """Combine results from multiple sentiment analysis methods"""
        if not methods_used:
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'confidence_score': 0.0
            }
        
        # Weight different methods
        weights = {
            'financial_keywords': 0.4,  # Most important for financial news
            'vader': 0.3,
            'textblob': 0.2,
            'transformer': 0.1
        }
        
        total_score = 0.0
        total_weight = 0.0
        confidence_scores = []
        
        # Combine scores from different methods
        for method in methods_used:
            if method in results and method in weights:
                method_result = results[method]
                weight = weights[method]
                
                total_score += method_result['score'] * weight
                total_weight += weight
                confidence_scores.append(method_result.get('confidence', 0.0))
        
        # Calculate final sentiment
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.0
        
        # Determine final label
        if final_score > 0.1:
            final_label = 'positive'
        elif final_score < -0.1:
            final_label = 'negative'
        else:
            final_label = 'neutral'
        
        # Calculate average confidence
        final_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            'sentiment_score': final_score,
            'sentiment_label': final_label,
            'confidence_score': final_confidence
        }
    
    def calculate_news_impact_score(self, sentiment_data: Dict[str, Any], headline: str) -> float:
        """Calculate impact score based on sentiment and headline characteristics"""
        impact_score = 0.0
        
        # Base impact from sentiment confidence
        impact_score += sentiment_data.get('confidence_score', 0.0) * 0.4
        
        # Impact from sentiment strength
        sentiment_score = abs(sentiment_data.get('sentiment_score', 0.0))
        impact_score += sentiment_score * 0.3
        
        # Impact from headline characteristics
        headline_lower = headline.lower()
        
        # Breaking news indicators
        breaking_indicators = ['breaking', 'urgent', 'alert', 'just in', 'exclusive']
        if any(indicator in headline_lower for indicator in breaking_indicators):
            impact_score += 0.2
        
        # Financial impact indicators
        impact_indicators = ['earnings', 'results', 'guidance', 'forecast', 'outlook', 'dividend', 'merger', 'acquisition']
        if any(indicator in headline_lower for indicator in impact_indicators):
            impact_score += 0.1
        
        # Ensure score is between 0 and 1
        return min(max(impact_score, 0.0), 1.0)

