"""
Unit tests for Order Block Analysis
"""

import unittest
import pandas as pd
import numpy as np
from src.others_analysis.order_blocks import OrderBlockAnalyzer, OrderBlock, OrderBlockType


class TestOrderBlockAnalyzer(unittest.TestCase):
    """Test cases for OrderBlockAnalyzer class"""
    
    def setUp(self):
        """Set up test data"""
        np.random.seed(42)
        
        # Create data with clear order blocks
        data = []
        for i in range(100):
            if i == 30:  # Bullish OB: down candle before up move
                data.append({'open': 100, 'high': 101, 'low': 98, 'close': 99})
            elif i == 31:  # Strong up move
                data.append({'open': 99, 'high': 105, 'low': 99, 'close': 104})
            elif i == 60:  # Bearish OB: up candle before down move
                data.append({'open': 104, 'high': 106, 'low': 104, 'close': 105})
            elif i == 61:  # Strong down move
                data.append({'open': 105, 'high': 105, 'low': 98, 'close': 99})
            else:
                price = 100 + np.random.normal(0, 1)
                data.append({
                    'open': price,
                    'high': price + abs(np.random.normal(0, 0.5)),
                    'low': price - abs(np.random.normal(0, 0.5)),
                    'close': price + np.random.normal(0, 0.3)
                })
        
        self.data = pd.DataFrame(data)
    
    def test_initialization(self):
        """Test OrderBlockAnalyzer initialization"""
        analyzer = OrderBlockAnalyzer(self.data)
        self.assertIsNotNone(analyzer.data)
        self.assertEqual(len(analyzer.order_blocks), 0)
    
    def test_invalid_data(self):
        """Test with invalid data"""
        invalid_data = pd.DataFrame({'price': [1, 2, 3]})
        with self.assertRaises(ValueError):
            OrderBlockAnalyzer(invalid_data)
    
    def test_identify_order_blocks(self):
        """Test order block identification"""
        analyzer = OrderBlockAnalyzer(self.data)
        order_blocks = analyzer.identify_order_blocks(min_move=0.01)
        
        self.assertIsInstance(order_blocks, list)
        self.assertTrue(len(order_blocks) > 0)
        
        # Check that we have both types
        types = [ob.type for ob in order_blocks]
        self.assertIn(OrderBlockType.BULLISH, types)
        self.assertIn(OrderBlockType.BEARISH, types)
    
    def test_order_block_properties(self):
        """Test order block properties"""
        analyzer = OrderBlockAnalyzer(self.data)
        order_blocks = analyzer.identify_order_blocks()
        
        if order_blocks:
            ob = order_blocks[0]
            self.assertIsInstance(ob, OrderBlock)
            self.assertIsInstance(ob.index, int)
            self.assertIsInstance(ob.top, (int, float))
            self.assertIsInstance(ob.bottom, (int, float))
            self.assertTrue(ob.top >= ob.bottom)
    
    def test_update_order_block_status(self):
        """Test order block status updates"""
        analyzer = OrderBlockAnalyzer(self.data)
        analyzer.identify_order_blocks()
        analyzer.update_order_block_status()
        
        # Some order blocks should be tested or broken
        tested_or_broken = any(ob.tested or ob.broken for ob in analyzer.order_blocks)
        self.assertTrue(tested_or_broken)
    
    def test_get_active_order_blocks(self):
        """Test getting active order blocks"""
        analyzer = OrderBlockAnalyzer(self.data)
        analyzer.identify_order_blocks()
        active_obs = analyzer.get_active_order_blocks()
        
        self.assertIsInstance(active_obs, list)
        # All active order blocks should not be broken
        self.assertTrue(all(not ob.broken for ob in active_obs))


if __name__ == '__main__':
    unittest.main()
