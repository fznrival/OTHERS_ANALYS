"""
Example usage of OTHERS Analysis
"""

import pandas as pd
import numpy as np
from others_analysis import OthersAnalyzer


def generate_sample_data(n_periods: int = 100) -> pd.DataFrame:
    """
    Generate sample OHLC data for testing.
    
    Args:
        n_periods: Number of periods to generate
        
    Returns:
        DataFrame with OHLC data
    """
    np.random.seed(42)
    
    # Generate a trending price series
    base_price = 100
    prices = [base_price]
    
    for i in range(n_periods - 1):
        # Add trend and noise
        trend = 0.05 if i < n_periods // 2 else -0.05
        change = np.random.normal(trend, 1)
        prices.append(prices[-1] + change)
    
    # Create OHLC data
    data = []
    for i, close in enumerate(prices):
        open_price = close + np.random.normal(0, 0.3)
        high = max(open_price, close) + abs(np.random.normal(0, 0.5))
        low = min(open_price, close) - abs(np.random.normal(0, 0.5))
        
        data.append({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': np.random.randint(1000, 10000)
        })
    
    return pd.DataFrame(data)


def main():
    """Run example OTHERS analysis"""
    
    print("Generating sample market data...")
    data = generate_sample_data(150)
    
    print("Initializing OTHERS Analyzer...")
    analyzer = OthersAnalyzer(data)
    
    print("\nPerforming comprehensive analysis...\n")
    
    # Get full analysis
    results = analyzer.analyze(
        identify_order_blocks=True,
        identify_liquidity_zones=True,
        detect_sweeps=True
    )
    
    # Print summary
    print(analyzer.get_analysis_summary())
    
    # Print detailed results
    print("\n\nDETAILED RESULTS:")
    print("=" * 50)
    
    print(f"\nOrder Blocks Identified: {len(results['order_blocks'])}")
    print(f"Active Order Blocks: {len(results['active_order_blocks'])}")
    
    if results['active_order_blocks']:
        print("\nActive Order Blocks Details:")
        for i, ob in enumerate(results['active_order_blocks'][:5], 1):
            print(f"  {i}. {ob['type'].title()} OB at index {ob['index']}")
            print(f"     Range: {ob['bottom']:.2f} - {ob['top']:.2f}")
            print(f"     Tested: {ob['tested']}")
    
    print(f"\nLiquidity Zones Identified: {len(results['liquidity_zones'])}")
    print(f"Active Liquidity Zones: {len(results['active_liquidity_zones'])}")
    
    if results['active_liquidity_zones']:
        print("\nActive Liquidity Zones Details:")
        for i, zone in enumerate(results['active_liquidity_zones'][:5], 1):
            print(f"  {i}. {zone['type'].title()} liquidity at index {zone['index']}")
            print(f"     Price: {zone['price']:.2f}")
            print(f"     Strength: {zone['strength']}")
    
    print(f"\nLiquidity Sweeps Detected: {len(results['liquidity_sweeps'])}")
    
    if results['liquidity_sweeps']:
        print("\nLiquidity Sweeps Details:")
        for i, sweep in enumerate(results['liquidity_sweeps'][:5], 1):
            print(f"  {i}. {sweep['type'].replace('_', ' ').title()} at index {sweep['index']}")
            print(f"     Price level: {sweep['price']:.2f}")
    
    # Get trading bias
    print("\n\nTRADING BIAS:")
    print("=" * 50)
    bias = analyzer.get_trading_bias()
    print(f"Direction: {bias['bias'].upper()}")
    print(f"Confidence: {bias['confidence'].upper()}")
    
    if bias['key_levels']:
        print("\nKey Levels:")
        for level_type, price in bias['key_levels'].items():
            print(f"  {level_type.title()}: {price:.2f}")
    
    print("\nReasoning:")
    for reason in bias['reasoning']:
        print(f"  - {reason}")
    
    print("\n" + "=" * 50)
    print("Analysis complete!")


if __name__ == "__main__":
    main()
