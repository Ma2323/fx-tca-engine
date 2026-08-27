import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_mock_fx_trades(n_trades=10000, seed=42):
    np.random.seed(seed)
    
    currency_pairs = {
        'EUR/USD': {'base_price': 1.0850, 'volatility': 0.0004},
        'GBP/USD': {'base_price': 1.2950, 'volatility': 0.0005},
        'USD/JPY': {'base_price': 155.20, 'volatility': 0.0800},
        'USD/CHF': {'base_price': 0.8850, 'volatility': 0.0003}
    }
    
    counterparties = ['Citi', 'JPMorgan', 'Barclays', 'Deutsche Bank', 'BNP Paribas', 'UBS']
    sides = ['BUY', 'SELL']
    
    start_time = datetime(2026, 1, 1, 8, 0, 0)
    timestamps = [start_time + timedelta(seconds=int(x)) for x in np.sort(np.random.uniform(0, 30 * 24 * 3600, n_trades))]
    
    records = []
    
    for i in range(n_trades):
        pair = np.random.choice(list(currency_pairs.keys()), p=[0.40, 0.30, 0.20, 0.10])
        base_info = currency_pairs[pair]
        
        side = np.random.choice(sides)
        counterparty = np.random.choice(counterparties)
        volume = np.random.choice([100_000, 250_000, 500_000, 1_000_000, 2_500_000, 5_000_000], 
                                  p=[0.30, 0.25, 0.20, 0.15, 0.07, 0.03])
        
        # Benchmark / Arrival Price
        arrival_price = base_info['base_price'] + np.random.normal(0, base_info['volatility'])
        
        # Latency & Slippage simulation
        latency_ms = int(np.random.exponential(scale=45) + 10)
        
        # Execution status simulation (94% filled, 6% rejected)
        status = np.random.choice(['FILLED', 'REJECTED'], p=[0.94, 0.06])
        
        if status == 'FILLED':
            # Price improvement or adverse slippage
            slippage_bps = np.random.normal(0.4, 0.9)  # Average 0.4 bps adverse slippage
            price_impact = (slippage_bps / 10000.0) * arrival_price
            
            if side == 'BUY':
                executed_price = arrival_price + price_impact
            else:
                executed_price = arrival_price - price_impact
        else:
            executed_price = np.nan
            
        records.append({
            'trade_id': f"TRD-{100000 + i}",
            'timestamp': timestamps[i],
            'currency_pair': pair,
            'side': side,
            'order_type': 'LIMIT',
            'volume': volume,
            'arrival_price': round(arrival_price, 5),
            'executed_price': round(executed_price, 5) if not np.isnan(executed_price) else None,
            'counterparty': counterparty,
            'latency_ms': latency_ms,
            'status': status
        })
        
    df = pd.DataFrame(records)
    df.to_csv('data/fx_execution_log.csv', index=False)
    print(f"Generated {n_trades} trade records saved to data/fx_execution_log.csv")

if __name__ == '__main__':
    generate_mock_fx_trades()