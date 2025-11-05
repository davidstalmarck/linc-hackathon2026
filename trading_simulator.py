import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ===== SIMULATE TRADING AND GENERATE ORDERS =====
class TradingSimulator:
    def __init__(self, stocks, initial_cash=100000):
        self.stocks = stocks
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.portfolio = {ticker: 0 for ticker in stocks}
        self.orders = []
        self.portfolio_snapshots = []
        self.prices_df = None  # Will store prices for plotting

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
        for ticker in self.stocks:
            snapshot[f'{ticker}_Shares'] = self.portfolio[ticker]
            snapshot[f'{ticker}_Value'] = self.portfolio[ticker] * prices_row[ticker]

        # Calculate total value
        total_holdings = sum(self.portfolio[ticker] * prices_row[ticker]
                           for ticker in self.stocks)
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
        """Plot portfolio performance vs individual stocks"""
        self.prices_df = prices_df
        portfolio_df = pd.DataFrame(self.portfolio_snapshots)

        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Main plot: Portfolio value vs stocks (normalized to start at 100)
        ax_main = fig.add_subplot(gs[0:2, :])

        # Normalize all values to start at 100 for comparison
        initial_portfolio_value = portfolio_df['Total_Value'].iloc[0]
        normalized_portfolio = (portfolio_df['Total_Value'] / initial_portfolio_value) * 100

        ax_main.plot(portfolio_df['Date'], normalized_portfolio,
                    label='Portfolio', linewidth=3, color='black', zorder=10)

        # Plot each stock normalized
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for idx, ticker in enumerate(self.stocks):
            initial_price = prices_df[ticker].iloc[0]
            normalized_stock = (prices_df[ticker] / initial_price) * 100
            ax_main.plot(prices_df['Date'], normalized_stock,
                        label=ticker, linewidth=2, alpha=0.7, color=colors[idx % len(colors)])

        ax_main.set_xlabel('Date', fontsize=12)
        ax_main.set_ylabel('Normalized Value (Start = 100)', fontsize=12)
        ax_main.set_title('Portfolio Performance vs Individual Stocks (Normalized)',
                         fontsize=14, fontweight='bold')
        ax_main.legend(loc='best', fontsize=10)
        ax_main.grid(True, alpha=0.3)

        # Calculate metrics
        final_value = portfolio_df['Total_Value'].iloc[-1]
        net_profit = final_value - self.initial_cash
        net_profit_pct = (net_profit / self.initial_cash) * 100
        sharpe_ratio = self.calculate_sharpe_ratio()

        # Subplot 1: Sharpe Ratio
        ax_sharpe = fig.add_subplot(gs[2, 0])
        sharpe_color = 'green' if sharpe_ratio > 0 else 'red'
        bars_sharpe = ax_sharpe.barh(['Sharpe Ratio'], [sharpe_ratio],
                                     color=sharpe_color, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax_sharpe.set_xlabel('Sharpe Ratio', fontsize=11)
        ax_sharpe.set_title(f'Sharpe Ratio: {sharpe_ratio:.3f}', fontsize=12, fontweight='bold')
        ax_sharpe.axvline(x=0, color='black', linestyle='-', linewidth=1.5)
        ax_sharpe.grid(True, alpha=0.3, axis='x')
        # Add value label
        ax_sharpe.text(sharpe_ratio, 0, f' {sharpe_ratio:.3f}',
                      va='center', ha='left' if sharpe_ratio < 0 else 'right',
                      fontsize=10, fontweight='bold')

        # Subplot 2: Net Profit/Loss
        ax_profit = fig.add_subplot(gs[2, 1])
        profit_color = 'green' if net_profit > 0 else 'red'
        bars_profit = ax_profit.barh(['Net P/L'], [net_profit_pct],
                                     color=profit_color, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax_profit.set_xlabel('Profit/Loss (%)', fontsize=11)
        ax_profit.set_title(f'Net P/L: ${net_profit:,.2f} ({net_profit_pct:+.2f}%)',
                           fontsize=12, fontweight='bold')
        ax_profit.axvline(x=0, color='black', linestyle='-', linewidth=1.5)
        ax_profit.grid(True, alpha=0.3, axis='x')
        # Add value label
        ax_profit.text(net_profit_pct, 0, f' {net_profit_pct:+.1f}%',
                      va='center', ha='left' if net_profit_pct < 0 else 'right',
                      fontsize=10, fontweight='bold')

        # Add summary text
        summary_text = f'Initial: ${self.initial_cash:,.0f}  |  Final: ${final_value:,.0f}  |  Trades: {len(self.orders)}'
        fig.text(0.5, 0.02, summary_text, ha='center', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.savefig(save_file, dpi=150, bbox_inches='tight')
        print(f"Saved performance plot to '{save_file}'")
        plt.close()

        # Print summary
        print(f"\n{'='*60}")
        print("TRADING SUMMARY")
        print(f"{'='*60}")
        print(f"Initial Cash: ${self.initial_cash:,.2f}")
        print(f"Final Value: ${final_value:,.2f}")
        print(f"Net Profit/Loss: ${net_profit:,.2f} ({net_profit_pct:+.2f}%)")
        print(f"Sharpe Ratio: {sharpe_ratio:.3f}")
        print(f"Total Trades: {len(self.orders)}")
        print(f"{'='*60}")
