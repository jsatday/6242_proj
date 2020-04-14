from scipy import signal
from trade_context import trade_context
import trade_context as tc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl


def macd_cross(df, start=0, end=-1, s_year=0, e_year=0):
	t_ctx = trade_context()

	for i in range(start, end):

		# Check the date range
		if s_year != 0 and int(df.Date[i][0:4]) < s_year:
			continue
		if e_year != 0 and int(df.Date[i][0:4]) > e_year:
			break

		# Buy the stock
		if (df.trend_macd[i] > df.trend_macd_signal[i] and
			not t_ctx.in_trade):

			tc.buy_stock(t_ctx, i, df.Close[i], df.trend_macd[i])
			continue

		# Sell the stock
		if (df.trend_macd[i] < df.trend_macd_signal[i] and
			t_ctx.in_trade):

			tc.sell_stock(t_ctx, i, df.Close[i], df.trend_macd[i])

	return t_ctx


def plot_macd_cross(df, t_ctx, start=0, end=-1):
	mpl.style.use('seaborn')

	fig, axs = plt.subplots(2, sharex=True)

	# Set the title
	axs[0].set_title("MACD Crossover")

	# Plot the price
	axs[0].plot(df[start:end].Close, label='Stock Price')

	# Plot the buys/sells on the price
	axs[0].plot(t_ctx.buy_times, t_ctx.buy_prices, 'ro', color='green', ms=5)
	axs[0].plot(t_ctx.sell_times, t_ctx.sell_prices, 'ro', color='red', ms=5)

	# Plot the MACDs
	axs[1].plot(df[start:end].trend_macd, label='MACD')
	axs[1].plot(df[start:end].trend_macd_signal, label='MACD Signal')
	
	# Plot the buys/sells on the MACD
	axs[1].plot(t_ctx.buy_times, t_ctx.buy_inds, 'ro', color='green', ms=5)
	axs[1].plot(t_ctx.sell_times, t_ctx.sell_inds, 'ro', color='red', ms=5)


def trade_with_macd_cross(df, start=0, end=-1, s_year=0, e_year=0, plot=False):
	# See if an end was given
	end = len(df.Close) if end==-1 else end

	# Simulate the Trades
	t_ctx = macd_cross(df, start, end, s_year, e_year)

	# Plot the data
	if plot:
		plot_macd_cross(df, t_ctx, start, end)

	return t_ctx
