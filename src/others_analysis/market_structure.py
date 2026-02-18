"""
Market Structure Analysis Module

Analyzes market structure to identify trends, breaks of structure, 
and changes of character.
"""

from enum import Enum
from typing import List, Optional, Tuple
import pandas as pd
import numpy as np


class Trend(Enum):
    """Market trend direction"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    RANGING = "ranging"


class StructureBreak(Enum):
    """Types of structure breaks"""
    BOS = "break_of_structure"  # Break of Structure
    CHoCH = "change_of_character"  # Change of Character


class MarketStructure:
    """
    Analyzes market structure to identify swing highs/lows, 
    breaks of structure, and trend direction.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize market structure analyzer.
        
        Args:
            data: DataFrame with OHLC data (columns: open, high, low, close)
        """
        if not all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            raise ValueError("Data must contain 'open', 'high', 'low', 'close' columns")
        
        self.data = data.copy()
        self.swing_highs = []
        self.swing_lows = []
        self.structure_breaks = []
        self.current_trend = Trend.RANGING
    
    def identify_swing_points(self, lookback: int = 5) -> Tuple[List[int], List[int]]:
        """
        Identify swing highs and lows in the price data.
        
        Args:
            lookback: Number of candles to look back for swing point validation
            
        Returns:
            Tuple of (swing_high_indices, swing_low_indices)
        """
        highs = self.data['high'].values
        lows = self.data['low'].values
        
        swing_highs = []
        swing_lows = []
        
        for i in range(lookback, len(self.data) - lookback):
            # Check for swing high
            is_swing_high = True
            for j in range(1, lookback + 1):
                if highs[i] <= highs[i - j] or highs[i] <= highs[i + j]:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_highs.append(i)
            
            # Check for swing low
            is_swing_low = True
            for j in range(1, lookback + 1):
                if lows[i] >= lows[i - j] or lows[i] >= lows[i + j]:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_lows.append(i)
        
        self.swing_highs = swing_highs
        self.swing_lows = swing_lows
        
        return swing_highs, swing_lows
    
    def identify_trend(self) -> Trend:
        """
        Identify the current market trend based on swing points.
        
        Returns:
            Current market trend
        """
        if not self.swing_highs or not self.swing_lows:
            self.identify_swing_points()
        
        if len(self.swing_highs) < 2 or len(self.swing_lows) < 2:
            return Trend.RANGING
        
        # Get recent swing points
        recent_highs = self.data.iloc[self.swing_highs[-2:]]['high'].values
        recent_lows = self.data.iloc[self.swing_lows[-2:]]['low'].values
        
        # Bullish: Higher Highs and Higher Lows
        higher_highs = recent_highs[-1] > recent_highs[-2]
        higher_lows = recent_lows[-1] > recent_lows[-2]
        
        # Bearish: Lower Highs and Lower Lows
        lower_highs = recent_highs[-1] < recent_highs[-2]
        lower_lows = recent_lows[-1] < recent_lows[-2]
        
        if higher_highs and higher_lows:
            self.current_trend = Trend.BULLISH
        elif lower_highs and lower_lows:
            self.current_trend = Trend.BEARISH
        else:
            self.current_trend = Trend.RANGING
        
        return self.current_trend
    
    def detect_structure_break(self, index: int) -> Optional[StructureBreak]:
        """
        Detect if a structure break occurred at the given index.
        
        Args:
            index: Index to check for structure break
            
        Returns:
            Type of structure break or None
        """
        if not self.swing_highs or not self.swing_lows:
            self.identify_swing_points()
        
        current_price = self.data.iloc[index]['close']
        
        # Check for bullish structure break (break above recent swing high)
        if self.current_trend == Trend.BEARISH or self.current_trend == Trend.RANGING:
            if self.swing_highs:
                last_swing_high = self.data.iloc[self.swing_highs[-1]]['high']
                if current_price > last_swing_high:
                    return StructureBreak.CHoCH if self.current_trend == Trend.BEARISH else StructureBreak.BOS
        
        # Check for bearish structure break (break below recent swing low)
        if self.current_trend == Trend.BULLISH or self.current_trend == Trend.RANGING:
            if self.swing_lows:
                last_swing_low = self.data.iloc[self.swing_lows[-1]]['low']
                if current_price < last_swing_low:
                    return StructureBreak.CHoCH if self.current_trend == Trend.BULLISH else StructureBreak.BOS
        
        return None
    
    def get_market_structure_summary(self) -> dict:
        """
        Get a summary of the current market structure.
        
        Returns:
            Dictionary containing market structure information
        """
        self.identify_swing_points()
        trend = self.identify_trend()
        
        return {
            'trend': trend.value,
            'swing_highs_count': len(self.swing_highs),
            'swing_lows_count': len(self.swing_lows),
            'last_swing_high': self.data.iloc[self.swing_highs[-1]]['high'] if self.swing_highs else None,
            'last_swing_low': self.data.iloc[self.swing_lows[-1]]['low'] if self.swing_lows else None,
        }
