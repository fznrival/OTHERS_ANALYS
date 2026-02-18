# OTHERS_ANALYS

A comprehensive Python library for **OTHERS analysis** using **ICT (Inner Circle Trader)** methodology. This tool helps traders analyze market structure, identify institutional order blocks, detect liquidity zones, and recognize stop hunts (liquidity sweeps).

## What is OTHERS?

**OTHERS** is an acronym representing key concepts in ICT trading methodology:

- **O**rder Blocks - Areas where institutional orders are placed
- **T**ime Frames - Multiple timeframe analysis
- **H**igher Time Frames - Understanding higher TF bias
- **E**qual Highs/Lows - Liquidity pool identification
- **R**elative Liquidity - Understanding where stops are placed
- **S**weeps - Stop hunts and liquidity grabs

## Features

- **Market Structure Analysis**: Identify swing highs/lows, breaks of structure (BOS), and changes of character (CHoCH)
- **Order Block Detection**: Automatically identify bullish and bearish order blocks
- **Liquidity Zone Identification**: Find equal highs/lows where liquidity is concentrated
- **Liquidity Sweep Detection**: Recognize stop hunts and liquidity grabs
- **Trading Bias**: Get actionable trading direction based on comprehensive analysis
- **Easy Integration**: Simple API for integration into your trading systems

## Installation

### From source:

```bash
git clone https://github.com/fznrival/OTHERS_ANALYS.git
cd OTHERS_ANALYS
pip install -r requirements.txt
pip install -e .
```

## Quick Start

```python
import pandas as pd
from others_analysis import OthersAnalyzer

# Load your OHLC data
data = pd.DataFrame({
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...]
})

# Create analyzer
analyzer = OthersAnalyzer(data)

# Perform comprehensive analysis
results = analyzer.analyze()

# Get trading bias
bias = analyzer.get_trading_bias()
print(f"Trading Bias: {bias['bias']}")
print(f"Confidence: {bias['confidence']}")

# Print summary
print(analyzer.get_analysis_summary())
```

## Example Output

```
==================================================
OTHERS ANALYSIS SUMMARY
==================================================

Market Trend: BULLISH
Swing Highs: 12
Swing Lows: 11

Total Order Blocks: 8
Active Order Blocks: 3
  Active OBs:
    - Bullish OB: 98.45 - 99.12
    - Bullish OB: 95.23 - 96.01
    - Bearish OB: 102.34 - 103.15

Total Liquidity Zones: 6
Active Liquidity Zones: 4
Liquidity Sweeps Detected: 2

TRADING BIAS:
  Direction: BULLISH
  Confidence: MEDIUM
  Key Levels:
    - Support: 98.45
    - Resistance: 105.67
  
  Reasoning:
    - Market structure is bullish (higher highs and higher lows)
    - Bullish order block support at 98.45
    - Buy-side liquidity target at 105.67

==================================================
```

## Usage Examples

### Basic Analysis

See the [examples/basic_usage.py](examples/basic_usage.py) file for a complete example:

```bash
cd examples
python basic_usage.py
```

### Component Usage

You can also use individual components:

```python
from others_analysis import MarketStructure, OrderBlockAnalyzer, LiquidityAnalyzer

# Market structure only
ms = MarketStructure(data)
trend = ms.identify_trend()
swing_highs, swing_lows = ms.identify_swing_points()

# Order blocks only
ob_analyzer = OrderBlockAnalyzer(data)
order_blocks = ob_analyzer.identify_order_blocks()
active_obs = ob_analyzer.get_active_order_blocks()

# Liquidity zones only
liq_analyzer = LiquidityAnalyzer(data)
liquidity_zones = liq_analyzer.identify_equal_highs_lows()
sweeps = liq_analyzer.detect_liquidity_sweeps()
```

## API Documentation

### OthersAnalyzer

Main class for comprehensive OTHERS analysis.

**Methods:**
- `analyze()`: Perform full analysis and return results dictionary
- `get_trading_bias()`: Get current trading bias with key levels
- `get_analysis_summary()`: Get human-readable summary string

### MarketStructure

Analyzes market structure and trends.

**Methods:**
- `identify_swing_points(lookback=5)`: Identify swing highs and lows
- `identify_trend()`: Determine current market trend
- `detect_structure_break(index)`: Detect BOS or CHoCH at given index

### OrderBlockAnalyzer

Identifies and tracks order blocks.

**Methods:**
- `identify_order_blocks(min_move=0.01)`: Identify all order blocks
- `get_active_order_blocks()`: Get valid (unbroken) order blocks
- `get_nearest_order_block(price, ob_type)`: Find nearest OB to a price

### LiquidityAnalyzer

Identifies liquidity zones and sweeps.

**Methods:**
- `identify_equal_highs_lows(tolerance=0.001)`: Find liquidity zones
- `detect_liquidity_sweeps()`: Detect stop hunts
- `get_active_liquidity_zones()`: Get unswept liquidity zones

## Requirements

- Python >= 3.7
- numpy >= 1.21.0
- pandas >= 1.3.0
- matplotlib >= 3.4.0 (for visualization)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and research purposes only. Trading financial instruments carries risk. Always do your own research and consult with a financial advisor before making trading decisions.

## Acknowledgments

Based on ICT (Inner Circle Trader) concepts and smart money analysis methodology. 
