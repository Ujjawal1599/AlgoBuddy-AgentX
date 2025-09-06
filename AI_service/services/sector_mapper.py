import asyncio
import aiohttp
import logging
from typing import Dict, Optional, List
import json

logger = logging.getLogger(__name__)

class SectorMapperService:
    def __init__(self):
        self.sector_mapping = self._load_static_mapping()
        
    def _load_static_mapping(self) -> Dict[str, str]:
        """Load static sector mapping for common Indian stocks"""
        return {
            # Technology
            'TCS': 'Technology',
            'INFY': 'Technology', 
            'WIPRO': 'Technology',
            'HCLTECH': 'Technology',
            'TECHM': 'Technology',
            'LTTS': 'Technology',
            'MINDTREE': 'Technology',
            'MPHASIS': 'Technology',
            'PERSISTENT': 'Technology',
            'COFORGE': 'Technology',
            
            # Banking
            'HDFCBANK': 'Banking',
            'ICICIBANK': 'Banking',
            'KOTAKBANK': 'Banking',
            'AXISBANK': 'Banking',
            'SBIN': 'Banking',
            'INDUSINDBK': 'Banking',
            'BANDHANBNK': 'Banking',
            'FEDERALBNK': 'Banking',
            'IDFCFIRSTB': 'Banking',
            'RBLBANK': 'Banking',
            
            # Pharmaceuticals
            'SUNPHARMA': 'Pharmaceuticals',
            'DRREDDY': 'Pharmaceuticals',
            'CIPLA': 'Pharmaceuticals',
            'LUPIN': 'Pharmaceuticals',
            'BIOCON': 'Pharmaceuticals',
            'DIVISLAB': 'Pharmaceuticals',
            'AUROPHARMA': 'Pharmaceuticals',
            'CADILAHC': 'Pharmaceuticals',
            'GLENMARK': 'Pharmaceuticals',
            'TORNTPHARM': 'Pharmaceuticals',
            
            # Automobile
            'MARUTI': 'Automobile',
            'TATAMOTORS': 'Automobile',
            'M&M': 'Automobile',
            'BAJAJ-AUTO': 'Automobile',
            'HEROMOTOCO': 'Automobile',
            'EICHERMOT': 'Automobile',
            'ASHOKLEY': 'Automobile',
            'TVSMOTORS': 'Automobile',
            'BOSCHLTD': 'Automobile',
            'EXIDEIND': 'Automobile',
            
            # Energy
            'RELIANCE': 'Energy',
            'ONGC': 'Energy',
            'IOC': 'Energy',
            'BPCL': 'Energy',
            'HPCL': 'Energy',
            'GAIL': 'Energy',
            'PETRONET': 'Energy',
            'ADANIGREEN': 'Energy',
            'TATAPOWER': 'Energy',
            'NTPC': 'Energy',
            
            # Telecom
            'BHARTIARTL': 'Telecom',
            'RCOM': 'Telecom',
            'IDEA': 'Telecom',
            'TATACOMM': 'Telecom',
            
            # FMCG
            'HINDUNILVR': 'FMCG',
            'ITC': 'FMCG',
            'NESTLEIND': 'FMCG',
            'DABUR': 'FMCG',
            'GODREJCP': 'FMCG',
            'MARICO': 'FMCG',
            'COLPAL': 'FMCG',
            'UBL': 'FMCG',
            'TITAN': 'FMCG',
            'TATACONSUM': 'FMCG',
            
            # Steel
            'TATASTEEL': 'Steel',
            'JSWSTEEL': 'Steel',
            'SAIL': 'Steel',
            'JINDALSTEL': 'Steel',
            'HINDALCO': 'Steel',
            'NMDC': 'Steel',
            'COALINDIA': 'Steel',
            'VEDL': 'Steel',
            
            # Cement
            'ULTRACEMCO': 'Cement',
            'SHREECEM': 'Cement',
            'GRASIM': 'Cement',
            'RAMCOCEM': 'Cement',
            'HEIDELBERG': 'Cement',
            'ORIENTCEM': 'Cement',
            'PRISM': 'Cement',
            'JKLAKSHMI': 'Cement',
            
            # Textiles
            'WELCORP': 'Textiles',
            'ARVIND': 'Textiles',
            'TRIDENT': 'Textiles',
            'GRASIM': 'Textiles',
            'RAYMOND': 'Textiles',
            'VARDHMAN': 'Textiles',
            'KPRMILL': 'Textiles',
            'WELSPUN': 'Textiles'
        }
    
    def get_sector(self, symbol: str) -> Optional[str]:
        """Get sector for a given stock symbol"""
        return self.sector_mapping.get(symbol.upper())
    
    def get_stocks_in_sector(self, sector: str) -> List[str]:
        """Get all stocks in a given sector"""
        return [symbol for symbol, sec in self.sector_mapping.items() if sec == sector]
    
    def get_all_sectors(self) -> List[str]:
        """Get list of all sectors"""
        return list(set(self.sector_mapping.values()))
    
    async def get_sector_from_api(self, symbol: str) -> Optional[str]:
        """Try to get sector from external API (NSE, etc.)"""
        try:
            # This would be implemented with actual API calls
            # For now, return from static mapping
            return self.get_sector(symbol)
        except Exception as e:
            logger.error(f"Error getting sector from API for {symbol}: {e}")
            return None

