#!/usr/bin/env python3
"""Generate demo transaction data for cashflow-radar testing.

Usage:
    python scripts/generate_demo_data.py --count 1000 --output data/demo.parquet
"""
import argparse
from datetime import datetime, timedelta
import random
import pandas as pd


def generate_transaction(
    txn_id: int,
    base_date: datetime,
    account_range: tuple[int, int] = (1, 100),
    amount_range: tuple[float, float] = (1000, 100000),
) -> dict:
    """Generate a single transaction record."""
    account_id = f"ACC{random.randint(*account_range):04d}"
    
    # Normal transactions
    amount = random.uniform(*amount_range)
    balance = random.uniform(100000, 1000000)
    
    # Inject anomalies based on txn_id patterns
    if txn_id % 50 == 0:
        # Large transaction anomaly
        amount *= 10
    elif txn_id % 30 == 0:
        # High frequency pattern (multiple small transactions)
        amount *= 0.1
    
    return {
        "transaction_id": f"TXN{txn_id:08d}",
        "account_id": account_id,
        "payee_id": f"ACC{random.randint(*account_range):04d}",
        "amount": round(amount, 2),
        "balance": round(balance, 2),
        "transaction_date": (base_date - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
        "transaction_time": (base_date - timedelta(hours=random.randint(0, 23))).strftime("%H:%M:%S"),
        "channel": random.choice(["柜台", "网银", "手机银行", "ATM"]),
        "transaction_type": random.choice(["转账", "支付", "提现", "缴费"]),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate demo transaction data")
    parser.add_argument("--count", type=int, default=1000, help="Number of transactions")
    parser.add_argument("--output", default="data/demo.parquet", help="Output file")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    
    random.seed(args.seed)
    
    print(f"Generating {args.count} transactions...")
    base_date = datetime.now()
    
    transactions = [
        generate_transaction(i, base_date)
        for i in range(1, args.count + 1)
    ]
    
    df = pd.DataFrame(transactions)
    df.to_parquet(args.output, index=False)
    print(f"Saved to {args.output}")
    print(f"\nData summary:")
    print(f"  Total transactions: {len(df)}")
    print(f"  Unique accounts: {df['account_id'].nunique()}")
    print(f"  Amount range: {df['amount'].min():.2f} - {df['amount'].max():.2f}")
    print(f"  Date range: {df['transaction_date'].min()} to {df['transaction_date'].max()}")


if __name__ == "__main__":
    main()
