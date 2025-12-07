# Database Schema Proposal

To accurately track money, holdings, and strategy performance, I propose the following 3 core tables.

## 1. `trades` (Transaction History)
The complete ledger of every action taken. This is the source of truth for "What happened?".

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Unique ID |
| `strategy_name` | String(50) | Which strategy initiated this (e.g., "RSI_Bot") |
| `ticker` | String(10) | Symbol (e.g., "AAPL") |
| `action` | Enum | 'BUY' or 'SELL' |
| `quantity` | Decimal(10, 4) | Number of shares |
| `price` | Decimal(10, 2) | Execution price per share |
| `total_cost` | Decimal(10, 2) | `(quantity * price) + fees` |
| `timestamp` | DateTime | When the trade happened |
| `order_id` | String(50) | Broker's Order ID (for reconciliation) |
| `status` | String(20) | 'FILLED', 'PENDING', 'FAILED' |

## 2. `strategies_holdings` (Stock Owned per Strategy)
To understand "each strategy's outcome," we should track holdings **per strategy**. If Strategy A buys AAPL and Strategy B buys AAPL, we track them separately so we know who is winning.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Unique ID |
| `strategy_name` | String(50) | The owner of this position |
| `ticker` | String(10) | Symbol |
| `quantity` | Decimal(10, 4) | Net shares held by this strategy |
| `average_price` | Decimal(10, 2) | Avg entry price (for calculating Performance) |
| `unrealized_pnl` | Decimal(10, 2) | `(current_price - avg_price) * quantity` |

## 3. `account_balance` (Account Money)
Allocating cash to strategies is complex. Usually, strategies share a cash pool, but we can track "Allocated" vs "Available".

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Single row (usually ID=1) |
| `total_cash` | Decimal(15, 2) | Cash available to trade |
| `total_equity` | Decimal(15, 2) | `Cash + Market Value of all Holdings` |
| `updated_at` | DateTime | Last sync with Broker |

---

### Key Questions for You:
1. **Shared vs. Segregated Cash**: Do you want strategies to have a hard "budget" (e.g., Strategy A gets $1000), or do they just dip into a shared global wallet?
2. **Holdings**: Do you agree with tracking holdings **per strategy**? (This allows you to see that Strategy A is up 10% on AAPL, even if Strategy B is down 5% on AAPL).
