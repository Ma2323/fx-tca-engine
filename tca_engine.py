import sqlite3
import pandas as pd
import numpy as np

class FXTCAEngine:
    def __init__(self, db_path='data/fx_treasury.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
    def load_csv_to_sql(self, csv_path='data/fx_execution_log.csv'):
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.to_sql('fx_trades', self.conn, if_exists='replace', index=False)
        print("Raw trade data successfully loaded into SQLite table: fx_trades")

    def run_query(self, query):
        return pd.read_sql_query(query, self.conn)

    def calculate_counterparty_metrics(self):
        query = """
        SELECT 
            counterparty,
            COUNT(*) as total_orders,
            SUM(CASE WHEN status = 'FILLED' THEN 1 ELSE 0 END) as filled_orders,
            SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected_orders,
            ROUND(100.0 * SUM(CASE WHEN status = 'FILLED' THEN 1 ELSE 0 END) / COUNT(*), 2) as fill_rate_pct,
            ROUND(SUM(CASE WHEN status = 'FILLED' THEN volume ELSE 0 END) / 1000000.0, 2) as filled_volume_millions,
            ROUND(AVG(latency_ms), 2) as avg_latency_ms
        FROM fx_trades
        GROUP BY counterparty
        ORDER BY filled_volume_millions DESC;
        """
        return self.run_query(query)

    def calculate_slippage_analysis(self):
        query = """
        SELECT 
            trade_id,
            timestamp,
            currency_pair,
            side,
            counterparty,
            volume,
            arrival_price,
            executed_price,
            latency_ms,
            CASE 
                WHEN side = 'BUY' THEN ((executed_price - arrival_price) / arrival_price) * 10000
                WHEN side = 'SELL' THEN ((arrival_price - executed_price) / arrival_price) * 10000
                ELSE 0
            END as slippage_bps
        FROM fx_trades
        WHERE status = 'FILLED';
        """
        return self.run_query(query)

    def get_aggregated_tca_summary(self):
        df_slippage = self.calculate_slippage_analysis()
        
        summary = df_slippage.groupby(['counterparty', 'currency_pair']).agg(
            total_trades=('trade_id', 'count'),
            total_volume=('volume', 'sum'),
            avg_slippage_bps=('slippage_bps', 'mean'),
            median_slippage_bps=('slippage_bps', 'median'),
            std_slippage_bps=('slippage_bps', 'std'),
            avg_latency_ms=('latency_ms', 'mean')
        ).reset_index()
        
        # Calculate Volume-Weighted Average Slippage
        summary['vw_avg_slippage_bps'] = (
            df_slippage.groupby(['counterparty', 'currency_pair'])
            .apply(lambda x: np.average(x['slippage_bps'], weights=x['volume']), include_groups=False)
            .values
        )
        return summary

if __name__ == '__main__':
    engine = FXTCAEngine()
    engine.load_csv_to_sql()
    print("\n--- Counterparty Execution Metrics ---")
    print(engine.calculate_counterparty_metrics())