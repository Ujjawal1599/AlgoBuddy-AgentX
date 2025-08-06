# Alpha Vantage API Setup Guide

## Error Resolution

The error you're seeing:
```
✗ Alpha Vantage failed: Alpha Vantage failed: Alpha Vantage error: Invalid API call. Please retry or visit the documentation (https://www.alphavantage.co/documentation/) for TIME_SERIES_INTRADAY.
```

This occurs because:
1. **Missing API Key**: Alpha Vantage requires a valid API key
2. **Rate Limiting**: Free tier has strict limits (5 calls per minute, 500 per day)
3. **Invalid Function**: The code was using `TIME_SERIES_INTRADAY` which has stricter limits

## Solution Steps

### 1. Get Alpha Vantage API Key

1. Go to [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Sign up for a free account
3. Get your API key from the dashboard

### 2. Configure Environment Variables

Edit the `AI_service/env` file:

```bash
# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY=your_actual_api_key_here
```

### 3. Load Environment Variables

Make sure your application loads the environment file:

```python
from dotenv import load_dotenv
load_dotenv('env')
```

### 4. Alternative Solutions

#### Option A: Use Mock Data (Recommended for Development)
The system now has improved fallback mechanisms:
- **Yahoo Finance**: Most reliable, no API key needed
- **Mock Data**: Always available, realistic data generation
- **Alpha Vantage**: Optional, requires API key

#### Option B: Disable Alpha Vantage
If you don't want to use Alpha Vantage, the system will automatically fall back to other sources.

## Data Source Priority

The system now tries data sources in this order:
1. **Yahoo Finance** (most reliable)
2. **CSV/Mock Data** (always available)
3. **Alpha Vantage** (requires API key)

## Testing the Fix

1. **Without API Key**: The system will skip Alpha Vantage and use other sources
2. **With API Key**: Alpha Vantage will be used as a backup data source

## Rate Limiting Information

- **Free Tier**: 5 calls per minute, 500 per day
- **Premium**: Higher limits available
- **Recommendation**: Use for development/testing only

## Error Messages Explained

- `"Invalid API call"`: Missing or invalid API key
- `"Note" in response`: Rate limit exceeded
- `"Error Message"`: Invalid symbol or other API error

## Troubleshooting

1. **Check API Key**: Ensure it's correctly set in environment
2. **Verify Symbol**: Some symbols may not be available
3. **Check Rate Limits**: Wait if you've exceeded limits
4. **Use Fallbacks**: The system will automatically try other sources

The improved error handling will now provide better feedback and automatically fall back to working data sources. 