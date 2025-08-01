from typing import Dict

from xno.analytics.performances import StrategyPerformance
import logging


class StrategyVisualizer:
    def __init__(self, df):
        self._bt_df = df
        self.name = None

    def performance_summary(self) -> Dict[str, float]:
        """
        Generate a summary of the algorithm's performance.

        :return: A dictionary containing performance metrics.
        """
        if not self._bt_df.empty:
            pf = StrategyPerformance(self._bt_df['step_ret'])
            return pf.summary
        else:
            logging.warning("No backtest data available for performance summary.")
            return {}

    def visualize(self):
        """
        Visualize the backtest results including:
        - Cumulative returns vs benchmark
        - Price with Buy/Sell signals
        - Metrics summary table
        """
        if self._bt_df is None or self._bt_df.empty:
            logging.warning("No backtest data available to visualize.")
            return

        df = self._bt_df.sort_index()
        performance = self.performance_summary()

        metric_names = list(sorted(performance.keys()))
        metric_values = [f"{performance[m]:.4f}" if isinstance(performance[m], float) else "-" for m in metric_names]

        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=2, cols=2,
            shared_xaxes=True,
            vertical_spacing=0.01,
            horizontal_spacing=0.01,
            column_widths=[0.8, 0.2],
            row_heights=[0.4, 0.6],
            subplot_titles=("Strategy vs Benchmark", "", "Price vs Signals", ""),
            specs=[[{"type": "xy"}, {"type": "table"}],
                   [{"type": "xy"}, None]]
        )

        # === Row 1: Strategy vs Benchmark ===
        fig.add_trace(go.Scatter(
            x=df.index, y=df['cum_ret'], mode='lines', name='Strategy',
            line=dict(color='blue')
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df.index, y=df['bm_cum_ret'], mode='lines', name='Benchmark',
            line=dict(color='gray', dash='dot')
        ), row=1, col=1)

        # === Row 2: Price with Buy/Sell signals ===
        fig.add_trace(go.Scatter(
            x=df.index, y=df['price'], mode='lines', name='Price',
            line=dict(color='black')
        ), row=2, col=1)

        # Buy markers
        buy_df = df[df['action'] == 'B'].copy()
        buy_df['date_str'] = buy_df.index.strftime('%Y-%m-%d')
        buy_df['time_str'] = buy_df.index.strftime('%H:%M:%S')
        # Format to string, 100000000 -> 100,000,000
        buy_df['balance_str'] = buy_df['equity'].apply(lambda x: f"{x:,.2f}")
        buy_df['amount_str'] = buy_df['amount'].apply(lambda x: f"{x:.2f}")
        buy_df['fee_str'] = buy_df['fee'].apply(lambda x: f"{x:.2f}")
        buy_df['price_str'] = buy_df['price'].apply(lambda x: f"{x:.2f}")
        fig.add_trace(go.Scatter(
            x=buy_df.index, y=buy_df['price'], mode='markers', name='Buy',
            marker=dict(symbol='triangle-up', color='green', size=10),
            hovertemplate="Buy [%{customdata[0]}]<br>"
                          "Time: %{customdata[1]}<br>"
                          "Price: %{customdata[2]}<br>"
                          "Amount: %{customdata[3]}<br>"
                          "Fee: %{customdata[4]}<br>"
                          "Balance: %{customdata[5]}"
                          "<extra></extra>",
            customdata=buy_df[['date_str', 'time_str', 'price_str', 'amount_str', 'fee_str', 'balance_str']].values
        ), row=2, col=1)

        # Sell markers
        sell_df = df[df['action'] == 'S'].copy()
        sell_df['date_str'] = sell_df.index.strftime('%Y-%m-%d')
        sell_df['time_str'] = sell_df.index.strftime('%H:%M:%S')
        # Format to string, 100000000 -> 100,000,000
        sell_df['balance_str'] = sell_df['equity'].apply(lambda x: f"{x:,.2f}")
        sell_df['amount_str'] = sell_df['amount'].apply(lambda x: f"{x:.2f}")
        sell_df['fee_str'] = sell_df['fee'].apply(lambda x: f"{x:.2f}")
        sell_df['price_str'] = sell_df['price'].apply(lambda x: f"{x:.2f}")
        fig.add_trace(go.Scatter(
            x=sell_df.index, y=sell_df['price'], mode='markers', name='Sell',
            marker=dict(symbol='triangle-down', color='red', size=10),
            hovertemplate="Sell [%{customdata[0]}]<br>"
                          "Time: %{customdata[1]}<br>"
                          "Price: %{customdata[2]}<br>"
                          "Amount: %{customdata[3]}<br>"
                          "Fee: %{customdata[4]}<br>"
                          "Balance: %{customdata[5]}"
                          "<extra></extra>",
            customdata=buy_df[['date_str', 'time_str', 'price_str', 'amount_str', 'fee_str', 'balance_str']].values
        ), row=2, col=1)

        # Latest annotation
        last_row = df.iloc[-1]
        fig.add_trace(go.Scatter(
            x=[last_row.index], y=[last_row['cum_ret']],
            mode='text', text=[f" - {last_row['cum_ret']:.2f}"],
            textposition='middle right',
            textfont=dict(color='blue', size=12), showlegend=False
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=[last_row.index], y=[last_row['bm_cum_ret']],
            mode='text', text=[f" - {last_row['bm_cum_ret']:.2f}"],
            textposition='middle right',
            textfont=dict(color='gray', size=12), showlegend=False
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=[last_row.index], y=[last_row['price']],
            mode='text', text=[f" - {last_row['price']:.2f}"],
            textposition='middle right',
            textfont=dict(color='black', size=12), showlegend=False
        ), row=2, col=1)

        # === Table ===
        fig.add_trace(go.Table(
            header=dict(
                values=["<b>Metric</b>", "<b>Value</b>"],
                fill_color="lightgray", align="left",
                font=dict(size=12)
            ),
            cells=dict(
                values=[metric_names, metric_values],
                fill_color="white", align="left",
                font=dict(size=12)
            )
        ), row=1, col=2)

        # === Layout ===
        fig.update_layout(
            title=f"Trading Strategy Performance: `{self.name}`",
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis2_title="Time",
            yaxis1_title="Cumulative Return",
            yaxis2_title="Price",
            template='plotly_white',
            hovermode='closest'
        )
        # Show the figure
        import IPython
        if IPython.get_ipython():
            fig.show()
        else:
            from IPython.utils import io
            with io.capture_output() as captured:
                fig.show()
