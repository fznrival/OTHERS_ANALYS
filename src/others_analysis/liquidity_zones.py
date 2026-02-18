"""
Liquidity Zone Analysis Module

Identifies and analyzes liquidity zones - areas where stops and orders 
are likely concentrated (equal highs/lows, liquidity pools).
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import pandas as pd
import numpy as np


class LiquidityType(Enum):
    """Type of liquidity zone"""
    BUY_SIDE = "buy_side"  # Above resistance, buy stops
    SELL_SIDE = "sell_side"  # Below support, sell stops


@dataclass
class LiquidityZone:
    """
    Represents a liquidity zone.
    
    Attributes:
        index: Index where the liquidity zone was identified
        type: Buy-side or sell-side liquidity
        price: Price level of the liquidity zone
        strength: Strength of the liquidity zone (number of touches)
        swept: Whether the liquidity has been swept
    """
    index: int
    type: LiquidityType
    price: float
    strength: int = 1
    swept: bool = False
    
    def is_active(self) -> bool:
        """Check if the liquidity zone is still active (not swept)"""
        return not self.swept


class LiquidityAnalyzer:
    """
    Analyzes price data to identify liquidity zones and sweeps.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize liquidity analyzer.
        
        Args:
            data: DataFrame with OHLC data (columns: open, high, low, close)
        """
        if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            raise ValueError("Data must contain 'open', 'high', 'low', 'close' columns")
        
        self.data = data.copy()
        self.liquidity_zones: List[LiquidityZone] = []
    
    def identify_equal_highs_lows(self, tolerance: float = 0.001) -> List[LiquidityZone]:
        """
        Identify equal highs and lows (liquidity zones).
        
        Args:
            tolerance: Price tolerance for considering levels "equal" (as percentage)
            
        Returns:
            List of identified liquidity zones
        """
        liquidity_zones = []
        
        # Identify equal highs (buy-side liquidity)
        for i in range(1, len(self.data) - 1):
            current_high = self.data.iloc[i]['high']
            
            # Look for nearby equal highs
            equal_count = 1
            for j in range(max(0, i - 5), min(len(self.data), i + 6)):
                if j == i:
                    continue
                
                other_high = self.data.iloc[j]['high']
                if abs(current_high - other_high) / current_high <= tolerance:
                    equal_count += 1
            
            if equal_count >= 2:
                zone = LiquidityZone(
                    index=i,
                    type=LiquidityType.BUY_SIDE,
                    price=current_high,
                    strength=equal_count
                )
                liquidity_zones.append(zone)
        
        # Identify equal lows (sell-side liquidity)
        for i in range(1, len(self.data) - 1):
            current_low = self.data.iloc[i]['low']
            
            # Look for nearby equal lows
            equal_count = 1
            for j in range(max(0, i - 5), min(len(self.data), i + 6)):
                if j == i:
                    continue
                
                other_low = self.data.iloc[j]['low']
                if abs(current_low - other_low) / current_low <= tolerance:
                    equal_count += 1
            
            if equal_count >= 2:
                zone = LiquidityZone(
                    index=i,
                    type=LiquidityType.SELL_SIDE,
                    price=current_low,
                    strength=equal_count
                )
                liquidity_zones.append(zone)
        
        # Remove duplicates (zones at similar prices)
        unique_zones = []
        for zone in liquidity_zones:
            is_duplicate = False
            for existing in unique_zones:
                if (zone.type == existing.type and
                    abs(zone.price - existing.price) / zone.price <= tolerance):
                    # Merge strength
                    if zone.strength > existing.strength:
                        existing.strength = zone.strength
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_zones.append(zone)
        
        self.liquidity_zones = unique_zones
        return unique_zones
    
    def detect_liquidity_sweeps(self) -> List[dict]:
        """
        Detect liquidity sweeps (stop hunts).
        
        A liquidity sweep occurs when price temporarily breaks through a liquidity zone
        and then reverses.
        
        Returns:
            List of detected sweeps with details
        """
        sweeps = []
        
        for zone in self.liquidity_zones:
            if zone.swept:
                continue
            
            # Check candles after the zone
            for i in range(zone.index + 1, len(self.data)):
                candle = self.data.iloc[i]
                
                if zone.type == LiquidityType.BUY_SIDE:
                    # Check for sweep above the high
                    if candle['high'] > zone.price:
                        # Check if it reversed (closed back below)
                        if candle['close'] < zone.price:
                            zone.swept = True
                            sweeps.append({
                                'index': i,
                                'type': 'buy_side_sweep',
                                'price': zone.price,
                                'wick_high': candle['high'],
                                'close': candle['close']
                            })
                            break
                
                elif zone.type == LiquidityType.SELL_SIDE:
                    # Check for sweep below the low
                    if candle['low'] < zone.price:
                        # Check if it reversed (closed back above)
                        if candle['close'] > zone.price:
                            zone.swept = True
                            sweeps.append({
                                'index': i,
                                'type': 'sell_side_sweep',
                                'price': zone.price,
                                'wick_low': candle['low'],
                                'close': candle['close']
                            })
                            break
        
        return sweeps
    
    def get_active_liquidity_zones(self) -> List[LiquidityZone]:
        """
        Get all active (not swept) liquidity zones.
        
        Returns:
            List of active liquidity zones
        """
        return [zone for zone in self.liquidity_zones if zone.is_active()]
    
    def get_nearest_liquidity(self, price: float, liq_type: Optional[LiquidityType] = None) -> Optional[LiquidityZone]:
        """
        Find the nearest active liquidity zone to a given price.
        
        Args:
            price: Price to search from
            liq_type: Optional filter for liquidity type
            
        Returns:
            Nearest liquidity zone or None
        """
        active_zones = self.get_active_liquidity_zones()
        
        if liq_type:
            active_zones = [zone for zone in active_zones if zone.type == liq_type]
        
        if not active_zones:
            return None
        
        return min(active_zones, key=lambda z: abs(z.price - price))
