"""
Main OTHERS Analyzer Module

Combines all ICT analysis components into a comprehensive analyzer.
OTHERS: Order blocks, Time frames, Higher time frames, Equal highs/lows, 
Relative liquidity, Sweeps
"""

from typing import Dict, List, Optional
import pandas as pd
from .market_structure import MarketStructure, Trend
from .order_blocks import OrderBlockAnalyzer, OrderBlock, OrderBlockType
from .liquidity_zones import LiquidityAnalyzer, LiquidityZone, LiquidityType


class OthersAnalyzer:
    """
    Comprehensive OTHERS analysis combining all ICT methodology components.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize OTHERS analyzer.
        
        Args:
            data: DataFrame with OHLC data (columns: open, high, low, close)
        """
        if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            raise ValueError("Data must contain 'open', 'high', 'low', 'close' columns")
        
        self.data = data.copy()
        self.market_structure = MarketStructure(data)
        self.order_block_analyzer = OrderBlockAnalyzer(data)
        self.liquidity_analyzer = LiquidityAnalyzer(data)
    
    def analyze(self, 
                identify_order_blocks: bool = True,
                identify_liquidity_zones: bool = True,
                detect_sweeps: bool = True) -> Dict:
        """
        Perform comprehensive OTHERS analysis.
        
        Args:
            identify_order_blocks: Whether to identify order blocks
            identify_liquidity_zones: Whether to identify liquidity zones
            detect_sweeps: Whether to detect liquidity sweeps
            
        Returns:
            Dictionary containing all analysis results
        """
        results = {
            'market_structure': None,
            'order_blocks': [],
            'active_order_blocks': [],
            'liquidity_zones': [],
            'active_liquidity_zones': [],
            'liquidity_sweeps': [],
        }
        
        # Market structure analysis
        results['market_structure'] = self.market_structure.get_market_structure_summary()
        
        # Order block analysis
        if identify_order_blocks:
            order_blocks = self.order_block_analyzer.identify_order_blocks()
            results['order_blocks'] = [
                {
                    'index': ob.index,
                    'type': ob.type.value,
                    'top': ob.top,
                    'bottom': ob.bottom,
                    'tested': ob.tested,
                    'broken': ob.broken,
                }
                for ob in order_blocks
            ]
            
            active_obs = self.order_block_analyzer.get_active_order_blocks()
            results['active_order_blocks'] = [
                {
                    'index': ob.index,
                    'type': ob.type.value,
                    'top': ob.top,
                    'bottom': ob.bottom,
                    'tested': ob.tested,
                }
                for ob in active_obs
            ]
        
        # Liquidity zone analysis
        if identify_liquidity_zones:
            liquidity_zones = self.liquidity_analyzer.identify_equal_highs_lows()
            results['liquidity_zones'] = [
                {
                    'index': zone.index,
                    'type': zone.type.value,
                    'price': zone.price,
                    'strength': zone.strength,
                    'swept': zone.swept,
                }
                for zone in liquidity_zones
            ]
            
            active_zones = self.liquidity_analyzer.get_active_liquidity_zones()
            results['active_liquidity_zones'] = [
                {
                    'index': zone.index,
                    'type': zone.type.value,
                    'price': zone.price,
                    'strength': zone.strength,
                }
                for zone in active_zones
            ]
        
        # Liquidity sweep detection
        if detect_sweeps:
            sweeps = self.liquidity_analyzer.detect_liquidity_sweeps()
            results['liquidity_sweeps'] = sweeps
        
        return results
    
    def get_trading_bias(self) -> Dict:
        """
        Get the current trading bias based on OTHERS analysis.
        
        Returns:
            Dictionary with trading bias and reasoning
        """
        trend = self.market_structure.identify_trend()
        active_obs = self.order_block_analyzer.get_active_order_blocks()
        active_liquidity = self.liquidity_analyzer.get_active_liquidity_zones()
        
        bias = {
            'trend': trend.value,
            'bias': 'neutral',
            'confidence': 'low',
            'key_levels': {},
            'reasoning': []
        }
        
        # Determine bias based on trend
        if trend == Trend.BULLISH:
            bias['bias'] = 'bullish'
            bias['confidence'] = 'medium'
            bias['reasoning'].append('Market structure is bullish (higher highs and higher lows)')
            
            # Find support levels (bullish order blocks)
            bullish_obs = [ob for ob in active_obs if ob.type == OrderBlockType.BULLISH]
            if bullish_obs:
                nearest_support = min(bullish_obs, key=lambda x: self.data.iloc[-1]['close'] - x.top)
                bias['key_levels']['support'] = nearest_support.top
                bias['reasoning'].append(f'Bullish order block support at {nearest_support.top:.2f}')
            
            # Find resistance (sell-side liquidity above)
            sell_side_liq = [z for z in active_liquidity if z.type == LiquidityType.BUY_SIDE]
            if sell_side_liq:
                nearest_resistance = min(sell_side_liq, key=lambda x: abs(x.price - self.data.iloc[-1]['close']))
                bias['key_levels']['resistance'] = nearest_resistance.price
                bias['reasoning'].append(f'Buy-side liquidity target at {nearest_resistance.price:.2f}')
        
        elif trend == Trend.BEARISH:
            bias['bias'] = 'bearish'
            bias['confidence'] = 'medium'
            bias['reasoning'].append('Market structure is bearish (lower highs and lower lows)')
            
            # Find resistance levels (bearish order blocks)
            bearish_obs = [ob for ob in active_obs if ob.type == OrderBlockType.BEARISH]
            if bearish_obs:
                nearest_resistance = min(bearish_obs, key=lambda x: x.bottom - self.data.iloc[-1]['close'])
                bias['key_levels']['resistance'] = nearest_resistance.bottom
                bias['reasoning'].append(f'Bearish order block resistance at {nearest_resistance.bottom:.2f}')
            
            # Find support (buy-side liquidity below)
            buy_side_liq = [z for z in active_liquidity if z.type == LiquidityType.SELL_SIDE]
            if buy_side_liq:
                nearest_support = min(buy_side_liq, key=lambda x: abs(x.price - self.data.iloc[-1]['close']))
                bias['key_levels']['support'] = nearest_support.price
                bias['reasoning'].append(f'Sell-side liquidity target at {nearest_support.price:.2f}')
        
        else:
            bias['reasoning'].append('Market is ranging - wait for clear direction')
        
        return bias
    
    def get_analysis_summary(self) -> str:
        """
        Get a human-readable summary of the analysis.
        
        Returns:
            String summary of the analysis
        """
        analysis = self.analyze()
        bias = self.get_trading_bias()
        
        summary = []
        summary.append("=" * 50)
        summary.append("OTHERS ANALYSIS SUMMARY")
        summary.append("=" * 50)
        summary.append("")
        
        # Market structure
        ms = analysis['market_structure']
        summary.append(f"Market Trend: {ms['trend'].upper()}")
        summary.append(f"Swing Highs: {ms['swing_highs_count']}")
        summary.append(f"Swing Lows: {ms['swing_lows_count']}")
        summary.append("")
        
        # Order blocks
        summary.append(f"Total Order Blocks: {len(analysis['order_blocks'])}")
        summary.append(f"Active Order Blocks: {len(analysis['active_order_blocks'])}")
        if analysis['active_order_blocks']:
            summary.append("  Active OBs:")
            for ob in analysis['active_order_blocks'][:3]:  # Show top 3
                summary.append(f"    - {ob['type'].title()} OB: {ob['bottom']:.2f} - {ob['top']:.2f}")
        summary.append("")
        
        # Liquidity zones
        summary.append(f"Total Liquidity Zones: {len(analysis['liquidity_zones'])}")
        summary.append(f"Active Liquidity Zones: {len(analysis['active_liquidity_zones'])}")
        summary.append(f"Liquidity Sweeps Detected: {len(analysis['liquidity_sweeps'])}")
        summary.append("")
        
        # Trading bias
        summary.append("TRADING BIAS:")
        summary.append(f"  Direction: {bias['bias'].upper()}")
        summary.append(f"  Confidence: {bias['confidence'].upper()}")
        if bias['key_levels']:
            summary.append("  Key Levels:")
            for level_type, price in bias['key_levels'].items():
                summary.append(f"    - {level_type.title()}: {price:.2f}")
        summary.append("")
        summary.append("  Reasoning:")
        for reason in bias['reasoning']:
            summary.append(f"    - {reason}")
        summary.append("")
        summary.append("=" * 50)
        
        return "\n".join(summary)
