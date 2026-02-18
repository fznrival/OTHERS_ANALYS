"""
Unit tests for Market Structure Analysis
"""

import unittest
import pandas as pd
import numpy as np
from src.others_analysis.market_structure import MarketStructure, Trend


class TestMarketStructure(unittest.TestCase):
    """Test cases for MarketStructure class"""
    
    def setUp(self):
        """Set up test data"""
        # Create bullish trending data
        np.random.seed(42)
        prices = [100 + i * 0.5 + np.random.normal(0, 0.5) for i in range(50)]
        
        self.bullish_data = pd.DataFrame({
            'open': [p + np.random.normal(0, 0.2) for p in prices],
            'high': [p + abs(np.random.normal(0, 0.5)) for p in prices],
            'low': [p - abs(np.random.normal(0, 0.5)) for p in prices],
            'close': prices
        })
        
        # Create bearish trending data
        prices = [100 - i * 0.5 + np.random.normal(0, 0.5) for i in range(50)]
        self.bearish_data = pd.DataFrame({
            'open': [p + np.random.normal(0, 0.2) for p in prices],
            'high': [p + abs(np.random.normal(0, 0.5)) for p in prices],
            'low': [p - abs(np.random.normal(0, 0.5)) for p in prices],
            'close': prices
        })
    
    def test_initialization(self):
        """Test MarketStructure initialization"""
        ms = MarketStructure(self.bullish_data)
        self.assertIsNotNone(ms.data)
        self.assertEqual(len(ms.data), 50)
    
    def test_invalid_data(self):
        """Test with invalid data"""
        invalid_data = pd.DataFrame({'price': [1, 2, 3]})
        with self.assertRaises(ValueError):
            MarketStructure(invalid_data)
    
    def test_identify_swing_points(self):
        """Test swing point identification"""
        ms = MarketStructure(self.bullish_data)
        highs, lows = ms.identify_swing_points(lookback=3)
        
        self.assertIsInstance(highs, list)
        self.assertIsInstance(lows, list)
        self.assertTrue(len(highs) > 0)
        self.assertTrue(len(lows) > 0)
    
    def test_identify_bullish_trend(self):
        """Test bullish trend identification"""
        ms = MarketStructure(self.bullish_data)
        trend = ms.identify_trend()
        
        # Should identify as bullish or ranging (due to noise)
        self.assertIn(trend, [Trend.BULLISH, Trend.RANGING])
    
    def test_identify_bearish_trend(self):
        """Test bearish trend identification"""
        ms = MarketStructure(self.bearish_data)
        trend = ms.identify_trend()
        
        # Should identify as bearish or ranging (due to noise)
        self.assertIn(trend, [Trend.BEARISH, Trend.RANGING])
    
    def test_get_market_structure_summary(self):
        """Test market structure summary"""
        ms = MarketStructure(self.bullish_data)
        summary = ms.get_market_structure_summary()
        
        self.assertIn('trend', summary)
        self.assertIn('swing_highs_count', summary)
        self.assertIn('swing_lows_count', summary)
        self.assertIsInstance(summary['swing_highs_count'], int)
        self.assertIsInstance(summary['swing_lows_count'], int)


if __name__ == '__main__':
    unittest.main()
