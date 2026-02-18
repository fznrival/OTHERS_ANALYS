"""
Unit tests for OTHERS Analyzer
"""

import unittest
import pandas as pd
import numpy as np
from src.others_analysis import OthersAnalyzer


class TestOthersAnalyzer(unittest.TestCase):
    """Test cases for OthersAnalyzer class"""
    
    def setUp(self):
        """Set up test data"""
        np.random.seed(42)
        prices = [100 + i * 0.2 + np.random.normal(0, 1) for i in range(100)]
        
        self.data = pd.DataFrame({
            'open': [p + np.random.normal(0, 0.3) for p in prices],
            'high': [p + abs(np.random.normal(0, 0.5)) for p in prices],
            'low': [p - abs(np.random.normal(0, 0.5)) for p in prices],
            'close': prices,
            'volume': [np.random.randint(1000, 10000) for _ in prices]
        })
    
    def test_initialization(self):
        """Test OthersAnalyzer initialization"""
        analyzer = OthersAnalyzer(self.data)
        self.assertIsNotNone(analyzer.data)
        self.assertIsNotNone(analyzer.market_structure)
        self.assertIsNotNone(analyzer.order_block_analyzer)
        self.assertIsNotNone(analyzer.liquidity_analyzer)
    
    def test_invalid_data(self):
        """Test with invalid data"""
        invalid_data = pd.DataFrame({'price': [1, 2, 3]})
        with self.assertRaises(ValueError):
            OthersAnalyzer(invalid_data)
    
    def test_analyze(self):
        """Test comprehensive analysis"""
        analyzer = OthersAnalyzer(self.data)
        results = analyzer.analyze()
        
        # Check that all expected keys are present
        expected_keys = [
            'market_structure',
            'order_blocks',
            'active_order_blocks',
            'liquidity_zones',
            'active_liquidity_zones',
            'liquidity_sweeps'
        ]
        
        for key in expected_keys:
            self.assertIn(key, results)
        
        # Check market structure
        self.assertIsInstance(results['market_structure'], dict)
        self.assertIn('trend', results['market_structure'])
        
        # Check order blocks
        self.assertIsInstance(results['order_blocks'], list)
        self.assertIsInstance(results['active_order_blocks'], list)
        
        # Check liquidity zones
        self.assertIsInstance(results['liquidity_zones'], list)
        self.assertIsInstance(results['active_liquidity_zones'], list)
        self.assertIsInstance(results['liquidity_sweeps'], list)
    
    def test_get_trading_bias(self):
        """Test trading bias calculation"""
        analyzer = OthersAnalyzer(self.data)
        bias = analyzer.get_trading_bias()
        
        # Check bias structure
        self.assertIn('trend', bias)
        self.assertIn('bias', bias)
        self.assertIn('confidence', bias)
        self.assertIn('key_levels', bias)
        self.assertIn('reasoning', bias)
        
        # Check bias values
        self.assertIn(bias['bias'], ['bullish', 'bearish', 'neutral'])
        self.assertIn(bias['confidence'], ['low', 'medium', 'high'])
        self.assertIsInstance(bias['reasoning'], list)
    
    def test_get_analysis_summary(self):
        """Test analysis summary generation"""
        analyzer = OthersAnalyzer(self.data)
        summary = analyzer.get_analysis_summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn('OTHERS ANALYSIS SUMMARY', summary)
        self.assertIn('Market Trend:', summary)
        self.assertIn('TRADING BIAS:', summary)
        self.assertTrue(len(summary) > 100)


if __name__ == '__main__':
    unittest.main()
