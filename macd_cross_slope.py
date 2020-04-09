from scipy import signal
from trade_context import trade_context
import trade_context as tc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl


def macd_cross_slope(df, start=0, end=-1):
	window_size = 15
	macd_smooth = []
	t_ctx = trade_context()

	for i in range(start, end):

		# Wait for enough data to start smoothing the curve
		if i-start >= window_size:
			macd_smooth = signal.savgol_filter(df.trend_macd[start:i+1], window_size, 1)
		else:
			continue

		# if i-start >= window_size:
		# 	macd_smooth.append(signal.savgol_filter(df.trend_macd[i-window_size+1:i+1], window_size, 1)[-1])
		# else:
		# 	macd_smooth.append(df.trend_macd[i])
		# 	continue

		#
		# Advanced rules
		#

		# Don't trade anything under 10
		if df.Close[i] < 10 and not t_ctx.in_trade:
			continue

		# if t_ctx.in_trade:
		# 	t_ctx.price_diff_cur = df.Close[i] - t_ctx.buy_price[-1]
		# 	price_diff_high = t_ctx.price_diff_cur if t_ctx.price_diff_cur > price_diff_high else price_diff_high
		# 	if t_ctx.price_diff_cur < price_diff_high/2:



		#
		# Typical entry and exit
		#

		# Buy the stock
		if (macd_smooth[-1]-macd_smooth[-2] > 0 and
			macd_smooth[-1] < df.trend_macd_signal[i] and
			not t_ctx.in_trade):

			tc.buy_stock(t_ctx, i, df.Close[i], macd_smooth[-1])
			continue

		# Sell the stock
		if (macd_smooth[-1]-macd_smooth[-2] < 0 and
			# macd_smooth[-1] > df.trend_macd_signal[i] and
			t_ctx.in_trade):

			tc.sell_stock(t_ctx, i, df.Close[i], macd_smooth[-1])
				
	return t_ctx, macd_smooth


def plot_macd_cross_slope(df, t_ctx, macd_smooth, start=0, end=-1):
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
	axs[1].plot([i for i in range(start,end)], macd_smooth, label='MACD Smooth', color='black')
	
	# Plot the buys/sells on the MACD
	axs[1].plot(t_ctx.buy_times, t_ctx.buy_inds, 'ro', color='green', ms=5)
	axs[1].plot(t_ctx.sell_times, t_ctx.sell_inds, 'ro', color='red', ms=5)


def trade_with_macd_cross_slope(df, start=0, end=-1, plot=False):
	# See if an end was given
	end = len(df.Close) if end==-1 else end

	# Simulate the Trades
	t_ctx, macd_smooth = macd_cross_slope(df, start, end)

	# Plot the data
	if plot:
		plot_macd_cross_slope(df, t_ctx, macd_smooth, start, end)

	return t_ctx
