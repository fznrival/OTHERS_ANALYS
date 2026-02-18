"""
Order Block Analysis Module

Identifies and analyzes order blocks - areas where institutional orders 
are believed to be placed.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import pandas as pd
import numpy as np


class OrderBlockType(Enum):
    """Type of order block"""
    BULLISH = "bullish"
    BEARISH = "bearish"


@dataclass
class OrderBlock:
    """
    Represents an order block zone.
    
    Attributes:
        index: Index of the candle that created the order block
        type: Bullish or bearish order block
        top: Upper boundary of the order block
        bottom: Lower boundary of the order block
        volume: Volume of the order block candle (if available)
        tested: Whether the order block has been tested
        broken: Whether the order block has been broken
    """
    index: int
    type: OrderBlockType
    top: float
    bottom: float
    volume: Optional[float] = None
    tested: bool = False
    broken: bool = False
    
    def is_valid(self) -> bool:
        """Check if the order block is valid (not broken)"""
        return not self.broken
    
    def contains_price(self, price: float) -> bool:
        """Check if a price is within the order block zone"""
        return self.bottom <= price <= self.top


class OrderBlockAnalyzer:
    """
    Analyzes price data to identify and track order blocks.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize order block analyzer.
        
        Args:
            data: DataFrame with OHLC data (columns: open, high, low, close)
        """
        if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            raise ValueError("Data must contain 'open', 'high', 'low', 'close' columns")
        
        self.data = data.copy()
        self.order_blocks: List[OrderBlock] = []
    
    def identify_order_blocks(self, min_move: float = 0.01) -> List[OrderBlock]:
        """
        Identify order blocks in the price data.
        
        An order block is typically the last down candle before a strong up move (bullish OB)
        or the last up candle before a strong down move (bearish OB).
        
        Args:
            min_move: Minimum percentage move required to consider an order block
            
        Returns:
            List of identified order blocks
        """
        order_blocks = []
        
        for i in range(1, len(self.data) - 1):
            current_candle = self.data.iloc[i]
            next_candle = self.data.iloc[i + 1]
            
            # Bullish order block: down candle followed by strong up move
            if (current_candle['close'] < current_candle['open'] and
                next_candle['close'] > next_candle['open']):
                
                move_size = (next_candle['close'] - next_candle['open']) / next_candle['open']
                
                if move_size >= min_move:
                    ob = OrderBlock(
                        index=i,
                        type=OrderBlockType.BULLISH,
                        top=current_candle['high'],
                        bottom=current_candle['low'],
                        volume=current_candle.get('volume', None)
                    )
                    order_blocks.append(ob)
            
            # Bearish order block: up candle followed by strong down move
            elif (current_candle['close'] > current_candle['open'] and
                  next_candle['close'] < next_candle['open']):
                
                move_size = (next_candle['open'] - next_candle['close']) / next_candle['open']
                
                if move_size >= min_move:
                    ob = OrderBlock(
                        index=i,
                        type=OrderBlockType.BEARISH,
                        top=current_candle['high'],
                        bottom=current_candle['low'],
                        volume=current_candle.get('volume', None)
                    )
                    order_blocks.append(ob)
        
        self.order_blocks = order_blocks
        return order_blocks
    
    def update_order_block_status(self) -> None:
        """
        Update the status of order blocks (tested/broken) based on subsequent price action.
        """
        for ob in self.order_blocks:
            if ob.broken:
                continue
            
            # Check subsequent candles
            for i in range(ob.index + 1, len(self.data)):
                candle = self.data.iloc[i]
                
                if ob.type == OrderBlockType.BULLISH:
                    # Check if price tested the order block (wick down into it)
                    if candle['low'] <= ob.top and candle['low'] >= ob.bottom:
                        ob.tested = True
                    
                    # Check if order block is broken (close below)
                    if candle['close'] < ob.bottom:
                        ob.broken = True
                        break
                
                elif ob.type == OrderBlockType.BEARISH:
                    # Check if price tested the order block (wick up into it)
                    if candle['high'] >= ob.bottom and candle['high'] <= ob.top:
                        ob.tested = True
                    
                    # Check if order block is broken (close above)
                    if candle['close'] > ob.top:
                        ob.broken = True
                        break
    
    def get_active_order_blocks(self) -> List[OrderBlock]:
        """
        Get all valid (not broken) order blocks.
        
        Returns:
            List of active order blocks
        """
        self.update_order_block_status()
        return [ob for ob in self.order_blocks if ob.is_valid()]
    
    def get_nearest_order_block(self, price: float, ob_type: Optional[OrderBlockType] = None) -> Optional[OrderBlock]:
        """
        Find the nearest valid order block to a given price.
        
        Args:
            price: Price to search from
            ob_type: Optional filter for order block type
            
        Returns:
            Nearest order block or None
        """
        active_obs = self.get_active_order_blocks()
        
        if ob_type:
            active_obs = [ob for ob in active_obs if ob.type == ob_type]
        
        if not active_obs:
            return None
        
        # Calculate distance from price to each order block
        def distance(ob: OrderBlock) -> float:
            if ob.bottom <= price <= ob.top:
                return 0
            elif price < ob.bottom:
                return ob.bottom - price
            else:
                return price - ob.top
        
        return min(active_obs, key=distance)
