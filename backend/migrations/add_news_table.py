"""
Migration script to add news_data table
Run this script to create the news_data table in your database
"""

from sqlalchemy import create_engine, text
from config.database import Base, engine
from models.news_data import NewsData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_news_table():
    """Create the news_data table"""
    try:
        # Create all tables (this will create news_data table)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Successfully created news_data table")
        
        # Verify table creation
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES LIKE 'news_data'"))
            if result.fetchone():
                logger.info("✅ news_data table verified in database")
            else:
                logger.error("❌ news_data table not found in database")
                
    except Exception as e:
        logger.error(f"❌ Error creating news_data table: {e}")
        raise

def drop_news_table():
    """Drop the news_data table (for testing)"""
    try:
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS news_data"))
            conn.commit()
        logger.info("✅ Successfully dropped news_data table")
    except Exception as e:
        logger.error(f"❌ Error dropping news_data table: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_news_table()
    else:
        create_news_table()

