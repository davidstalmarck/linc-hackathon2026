import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ===== SIMULATE TRADING AND GENERATE ORDERS =====
class TradingSimulator:
    def __init__(self, assets):
        self.assets = assets
        self.cash = 100000
        self.initial_cash = 100000
        self.portfolio = {ticker: 0 for ticker in assets}
        self.orders = []
        self.portfolio_snapshots = []
        self.prices_df = None  # Will store prices for plotting

    def execute_order(self, date, ticker, action, shares, price):
        """Execute a buy/sell order and record it."""
        action = action.upper()
        if shares <= 0:
            return False

        if action == 'BUY' and self.cash >= price * shares:
            cost = price * shares
            self.cash -= cost
            self.portfolio[ticker] += shares
            self.orders.append({
                'Date': date,
                'Ticker': ticker,
                'Action': 'BUY',
                'Shares': shares,
                'Price': price,
                'Total': cost
            })
            return True

        if action == 'SELL' and self.portfolio[ticker] >= shares:
            proceeds = price * shares
            self.cash += proceeds
            self.portfolio[ticker] -= shares
            self.orders.append({
                'Date': date,
                'Ticker': ticker,
                'Action': 'SELL',
                'Shares': shares,
                'Price': price,
                'Total': proceeds
            })
            return True

        return False

    def run(self, strategy_fn, prices_df, data):
        """Run a strategy function that returns a list of orders per day."""
        for idx, row in prices_df.iterrows():
            date = row['Date']
            prices = {ticker: row[ticker] for ticker in self.assets}
            orders = strategy_fn(
                date,
                self.cash,
                self.portfolio.copy(),
                prices,
                data["stocks"],
                data["indexes"],
                data["commodities"],
                data["currencies"]
            ) or []

            if isinstance(orders, tuple):
                orders = [orders]

            for action, ticker, shares in orders:
                price = prices[ticker]
                self.execute_order(date, ticker, action, shares, price)

            self.record_portfolio(date, prices)

    def execute_trade(self, date, ticker, signal, price):
        """Execute trade and record order"""
        shares = 10

        if signal == 1 and self.cash >= price * shares:
            # BUY ORDER
            cost = price * shares
            self.cash -= cost
            self.portfolio[ticker] += shares
            self.orders.append({
                'Date': date,
                'Ticker': ticker,
                'Action': 'BUY',
                'Shares': shares,
                'Price': price,
                'Total': cost
            })
            return True

        elif signal == -1 and self.portfolio[ticker] >= shares:
            # SELL ORDER
            proceeds = price * shares
            self.cash += proceeds
            self.portfolio[ticker] -= shares
            self.orders.append({
                'Date': date,
                'Ticker': ticker,
                'Action': 'SELL',
                'Shares': shares,
                'Price': price,
                'Total': proceeds
            })
            return True

        return False

    def record_portfolio(self, date, prices_row):
        """Record portfolio snapshot"""
        snapshot = {'Date': date, 'Cash': self.cash}

        # Add holdings for each stock
        for ticker in self.assets:
            snapshot[f'{ticker}_Shares'] = self.portfolio[ticker]
            snapshot[f'{ticker}_Value'] = self.portfolio[ticker] * prices_row[ticker]

        # Calculate total value
        total_holdings = sum(self.portfolio[ticker] * prices_row[ticker]
                           for ticker in self.assets)
        snapshot['Total_Value'] = self.cash + total_holdings

        self.portfolio_snapshots.append(snapshot)

    def save_results(self, orders_file='orders.csv', portfolio_file='portfolio.csv'):
        """Save orders and portfolio to CSV files"""
        # Save orders
        orders_df = pd.DataFrame(self.orders)
        orders_df.to_csv(orders_file, index=False)
        print(f"Saved {len(orders_df)} orders to '{orders_file}'")

        # Save portfolio
        portfolio_df = pd.DataFrame(self.portfolio_snapshots)
        portfolio_df.to_csv(portfolio_file, index=False)
        print(f"Saved {len(portfolio_df)} portfolio snapshots to '{portfolio_file}'")

    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        """Calculate Sharpe ratio from portfolio returns"""
        portfolio_df = pd.DataFrame(self.portfolio_snapshots)
        returns = portfolio_df['Total_Value'].pct_change().dropna()

        if len(returns) == 0:
            return 0

        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        if excess_returns.std() == 0:
            return 0

        sharpe_ratio = np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
        return sharpe_ratio

    def plot_performance(self, prices_df, save_file='performance_plot.png'):
        """Plot portfolio performance vs individual tickers"""
        self.prices_df = prices_df
        portfolio_df = pd.DataFrame(self.portfolio_snapshots)

        # Calculate rolling Sharpe ratio and cumulative profit/loss over time
        returns = portfolio_df['Total_Value'].pct_change().dropna()
        risk_free_rate = 0.02 / 252  # Daily risk-free rate

        # Rolling Sharpe ratio (30-day window)
        rolling_window = 30
        rolling_sharpe = []
        for i in range(len(returns)):
            if i < rolling_window:
                rolling_sharpe.append(np.nan)
            else:
                window_returns = returns.iloc[i-rolling_window:i]
                excess_returns = window_returns - risk_free_rate
                if excess_returns.std() > 0:
                    sharpe = np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
                else:
                    sharpe = 0
                rolling_sharpe.append(sharpe)

        # Cumulative profit/loss over time
        cumulative_pnl = ((portfolio_df['Total_Value'] - self.initial_cash) / self.initial_cash) * 100

        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Main plot: Portfolio value vs tickers (normalized to start at 100)
        ax_main = fig.add_subplot(gs[0, :])

        # Normalize all values to start at 100 for comparison
        initial_portfolio_value = portfolio_df['Total_Value'].iloc[0]
        normalized_portfolio = (portfolio_df['Total_Value'] / initial_portfolio_value) * 100

        ax_main.plot(portfolio_df['Date'], normalized_portfolio,
                    label='Portfolio', linewidth=3, color='black', zorder=10)

        # Plot each stock normalized
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for idx, ticker in enumerate(self.assets):
            initial_price = prices_df[ticker].iloc[0]
            normalized_stock = (prices_df[ticker] / initial_price) * 100
            ax_main.plot(prices_df['Date'], normalized_stock,
                        label=ticker, linewidth=2, alpha=0.7, color=colors[idx % len(colors)])

        ax_main.set_xlabel('Date', fontsize=12)
        ax_main.set_ylabel('Normalized Value (Start = 100)', fontsize=12)
        ax_main.set_title('Portfolio Performance vs Individual Tickers (Normalized)',
                         fontsize=14, fontweight='bold')
        ax_main.legend(loc='best', fontsize=10)
        ax_main.grid(True, alpha=0.3)

        # Calculate final metrics
        final_value = portfolio_df['Total_Value'].iloc[-1]
        net_profit = final_value - self.initial_cash
        net_profit_pct = (net_profit / self.initial_cash) * 100
        final_sharpe_ratio = self.calculate_sharpe_ratio()

        # Subplot 1: Rolling Sharpe Ratio over time
        ax_sharpe = fig.add_subplot(gs[1, 0])
        # Align with portfolio_df dates (skip first return)
        sharpe_dates = portfolio_df['Date'].iloc[1:]
        ax_sharpe.plot(sharpe_dates, rolling_sharpe, color='blue', linewidth=2)
        ax_sharpe.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax_sharpe.axhline(y=1, color='green', linestyle='--', linewidth=1, alpha=0.3, label='Good (>1)')
        ax_sharpe.axhline(y=-1, color='red', linestyle='--', linewidth=1, alpha=0.3, label='Poor (<-1)')
        ax_sharpe.set_xlabel('Date', fontsize=11)
        ax_sharpe.set_ylabel('Rolling Sharpe Ratio (30d)', fontsize=11)
        ax_sharpe.set_title(f'Rolling Sharpe Ratio (Final: {final_sharpe_ratio:.3f})',
                           fontsize=12, fontweight='bold')
        ax_sharpe.legend(loc='best', fontsize=9)
        ax_sharpe.grid(True, alpha=0.3)

        # Subplot 2: Cumulative Profit/Loss over time
        ax_profit = fig.add_subplot(gs[1, 1])
        profit_color = cumulative_pnl.apply(lambda x: 'green' if x >= 0 else 'red')
        ax_profit.plot(portfolio_df['Date'], cumulative_pnl, color='darkblue', linewidth=2)
        ax_profit.fill_between(portfolio_df['Date'], 0, cumulative_pnl,
                              where=(cumulative_pnl >= 0), color='green', alpha=0.3, interpolate=True)
        ax_profit.fill_between(portfolio_df['Date'], 0, cumulative_pnl,
                              where=(cumulative_pnl < 0), color='red', alpha=0.3, interpolate=True)
        ax_profit.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
        ax_profit.set_xlabel('Date', fontsize=11)
        ax_profit.set_ylabel('Cumulative P/L (%)', fontsize=11)
        ax_profit.set_title(f'Cumulative Profit/Loss (Final: ${net_profit:,.2f} / {net_profit_pct:+.2f}%)',
                           fontsize=12, fontweight='bold')
        ax_profit.grid(True, alpha=0.3)

        # Subplot 3: Trade distribution
        ax_trades = fig.add_subplot(gs[2, :])
        if len(self.orders) > 0:
            orders_df = pd.DataFrame(self.orders)
            buy_orders = orders_df[orders_df['Action'] == 'BUY']
            sell_orders = orders_df[orders_df['Action'] == 'SELL']

            for ticker in self.assets:
                ticker_buys = buy_orders[buy_orders['Ticker'] == ticker]
                ticker_sells = sell_orders[sell_orders['Ticker'] == ticker]

                if len(ticker_buys) > 0:
                    ax_trades.scatter(ticker_buys['Date'], ticker_buys['Price'],
                                    marker='^', s=50, alpha=0.6, label=f'{ticker} Buy')
                if len(ticker_sells) > 0:
                    ax_trades.scatter(ticker_sells['Date'], ticker_sells['Price'],
                                    marker='v', s=50, alpha=0.6, label=f'{ticker} Sell')

            ax_trades.set_xlabel('Date', fontsize=11)
            ax_trades.set_ylabel('Price ($)', fontsize=11)
            ax_trades.set_title(f'Trade Execution Points (Total: {len(self.orders)} trades)',
                               fontsize=12, fontweight='bold')
            ax_trades.legend(loc='best', fontsize=9, ncol=4)
            ax_trades.grid(True, alpha=0.3)
        else:
            ax_trades.text(0.5, 0.5, 'No trades executed', ha='center', va='center',
                          fontsize=14, transform=ax_trades.transAxes)

        # Add summary text
        summary_text = f'Initial: ${self.initial_cash:,.0f}  |  Final: ${final_value:,.0f}  |  Trades: {len(self.orders)}'
        fig.text(0.5, 0.02, summary_text, ha='center', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.savefig(save_file, dpi=150, bbox_inches='tight')
        print(f"Saved performance plot to '{save_file}'")
        plt.show()  # Display the plot
        plt.close()

        # Print summary
        print(f"\n{'='*60}")
        print("TRADING SUMMARY")
        print(f"{'='*60}")
        print(f"Initial Cash: ${self.initial_cash:,.2f}")
        print(f"Final Value: ${final_value:,.2f}")
        print(f"Net Profit/Loss: ${net_profit:,.2f} ({net_profit_pct:+.2f}%)")
        print(f"Sharpe Ratio: {final_sharpe_ratio:.3f}")
        print(f"Total Trades: {len(self.orders)}")
        print(f"{'='*60}")
