from scipy import signal
from trade_context import trade_context
import trade_context as tc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl


def macd_diff_smooth(df, start=0, end=-1):
	window_size = 7
	macd_diff_data = []
	macd_diff_smooth_data = []
	t_ctx = trade_context()
	
	for i in range(start, end):
		macd_diff_data.append(df.trend_macd_diff[i])

		# Wait for enough data to start smoothing the curve
		if i-start > window_size:
			macd_diff_smooth_data = signal.savgol_filter(macd_diff_data, window_size, 1)
		else:
			continue

		# Buy the stock
		if (macd_diff_smooth_data[-1]-macd_diff_smooth_data[-2] > 0 and
			# df.trend_macd[i] < df.trend_macd_signal[i] and
			not t_ctx.in_trade):

			tc.buy_stock(t_ctx, i, df.Close[i], macd_diff_smooth_data[-1])
			continue

		# Sell the stock
		if (macd_diff_smooth_data[-1]-macd_diff_smooth_data[-2] <= 0 and 
			# df.trend_macd[i] > df.trend_macd_signal[i] and
			t_ctx.in_trade):

			tc.sell_stock(t_ctx, i, df.Close[i], macd_diff_smooth_data[-1])

	return t_ctx, macd_diff_smooth_data


def plot_macd_diff_smooth(df, t_ctx, macd_diff_smooth_data, start=0, end=-1):
	mpl.style.use('seaborn')

	fig, axs = plt.subplots(2, sharex=True)

	# Set the title
	axs[0].set_title("MACD Difference Smooth")

	# Plot the price
	axs[0].plot(df[start:end].Close, label='Stock Price')

	# Plot the buys/sells on the price
	axs[0].plot(t_ctx.buy_times, t_ctx.buy_prices, 'ro', color='green', ms=5)
	axs[0].plot(t_ctx.sell_times, t_ctx.sell_prices, 'ro', color='red', ms=5)

	# Plot the MACDs
	axs[1].plot(df[start:end].trend_macd, label='MACD')
	axs[1].plot(df[start:end].trend_macd_signal, label='MACD Signal')
	axs[1].plot(df[start:end].trend_macd_diff, label='MACD Difference')
	axs[1].plot([i for i in range(start,end)], macd_diff_smooth_data, label='MACD Difference Smooth', color='black')

	# Plot the buys/sells on the MACD diff smooth
	axs[1].plot(t_ctx.buy_times, t_ctx.buy_inds, 'ro', color='green', ms=5)
	axs[1].plot(t_ctx.sell_times, t_ctx.sell_inds, 'ro', color='red', ms=5)


def trade_with_macd_diff_smooth(df, start=0, end=-1, plot=False):
	# See if an end was given
	end = len(df.Close) if end==-1 else end

	# Simulate the Trades
	t_ctx, macd_diff_smooth_data = macd_diff_smooth(df, start, end)

	# Plot the data
	if plot:
		plot_macd_diff_smooth(df, t_ctx, macd_diff_smooth_data, start, end)

	return t_ctx
