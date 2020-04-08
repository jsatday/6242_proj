from scipy import signal
from trade_points import trade_points
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl


def macd_diff_smooth(df, start=0, end=-1):
	in_trade = False
	window_size = 7
	macd_diff_data = []
	macd_diff_smooth_values = []
	itrades = trade_points([],[],[],[])
	ptrades = trade_points([],[],[],[])
	
	for i in range(start,end):
		macd_diff_data.append(df.trend_macd_diff[i])

		# Wait for enough data to start smoothing the curve
		if len(macd_diff_data) > window_size:
			macd_diff_smooth_values = signal.savgol_filter(macd_diff_data, window_size, 1)

			# Buy the stock
			if (macd_diff_smooth_values[-1]-macd_diff_smooth_values[-2] > 0 and
				df.trend_macd[i] < df.trend_macd_signal[i] and
				not in_trade):

				in_trade = True
				itrades.buy_xs.append(i)
				itrades.buy_ys.append(macd_diff_smooth_values[-1])
				ptrades.buy_xs.append(i)
				ptrades.buy_ys.append(df.Close[i])
				continue

			# Sell the stock
			if (macd_diff_smooth_values[-1]-macd_diff_smooth_values[-2] <= 0 and 
				df.trend_macd[i] > df.trend_macd_signal[i] and
				in_trade):

				in_trade = False
				itrades.sell_xs.append(i)
				itrades.sell_ys.append(macd_diff_smooth_values[-1])
				ptrades.sell_xs.append(i)
				ptrades.sell_ys.append(df.Close[i])

	return ptrades, itrades, macd_diff_smooth_values


def plot_macd_diff_smooth(df, ptrades, itrades, macd_diff_smooth_values, start=0, end=-1):
	mpl.style.use('seaborn')

	fig, axs = plt.subplots(2, sharex=True)

	# Set the title
	axs[0].set_title("MACD Difference Smooth")

	# Plot the price
	axs[0].plot(df[start:end].Close, label='Stock Price')

	# Plot the buys/sells on the price
	axs[0].plot(ptrades.buy_xs, ptrades.buy_ys, 'ro', color='green', ms=5)
	axs[0].plot(ptrades.sell_xs, ptrades.sell_ys, 'ro', color='red', ms=5)

	# Plot the MACDs
	axs[1].plot(df[start:end].trend_macd, label='MACD')
	axs[1].plot(df[start:end].trend_macd_signal, label='MACD Signal')
	axs[1].plot(df[start:end].trend_macd_diff, label='MACD Difference')
	axs[1].plot([i for i in range(start,end)], macd_diff_smooth_values, label='MACD Difference Smooth', color='black')

	# Plot the buys/sells on the MACD diff smooth
	axs[1].plot(itrades.buy_xs, itrades.buy_ys, 'ro', color='green', ms=5)
	axs[1].plot(itrades.sell_xs, itrades.sell_ys, 'ro', color='red', ms=5)


def trade_with_macd_diff_smooth(df, start=0, end=-1, plot=False):
	# See if an end was given
	end = len(df.Close) if end==-1 else end

	# Simulate the Trades
	ptrades, itrades, macd_diff_smooth_values = macd_diff_smooth(df, start, end)

	# Plot the data
	if plot:
		plot_macd_diff_smooth(df, ptrades, itrades, macd_diff_smooth_values, start, end)
		plt.show()

	return ptrades
