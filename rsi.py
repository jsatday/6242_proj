from scipy import signal
from trade_context import trade_context
import trade_context as tc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl


def rsi(df, start=0, end=-1):
	t_ctx = trade_context()

	for i in range(start, end):

		# Buy the stock
		if (df.momentum_rsi[i] < 30 and
			not t_ctx.in_trade):

			tc.buy_stock(t_ctx, i, df.Close[i], df.momentum_rsi[i])
			continue

		# Sell the stock
		if (df.momentum_rsi[i] > 70 and
			t_ctx.in_trade):

			tc.sell_stock(t_ctx, i, df.Close[i], df.momentum_rsi[i])

	return t_ctx


def plot_rsi(df, t_ctx, start=0, end=-1):
	mpl.style.use('seaborn')

	fig, axs = plt.subplots(2, sharex=True)

	# Set the title
	axs[0].set_title("RSI")

	# Plot the price
	axs[0].plot(df[start:end].Close, label='Stock Price')

	# Plot the buys/sells on the price
	axs[0].plot(t_ctx.buy_times, t_ctx.buy_prices, 'ro', color='green', ms=5)
	axs[0].plot(t_ctx.sell_times, t_ctx.sell_prices, 'ro', color='red', ms=5)

	# Plot the RSI
	axs[1].plot(df[start:end].momentum_rsi, label='RSI')
	#axs[1].plot(df[start:end].trend_macd_signal, label='MACD Signal')
	
	# Plot the buys/sells on the RSI
	axs[1].plot(t_ctx.buy_times, t_ctx.buy_inds, 'ro', color='green', ms=5)
	axs[1].plot(t_ctx.sell_times, t_ctx.sell_inds, 'ro', color='red', ms=5)


def trade_with_rsi(df, start=0, end=-1, plot=False):
	# See if an end was given
	end = len(df.Close) if end==-1 else end

	# Simulate the Trades
	t_ctx = rsi(df, start, end)

	# Plot the data
	if plot:
		plot_rsi(df, t_ctx, start, end)

	return t_ctx