from scipy import signal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

class Indicator_Trades():
	def __init__(self, buy_xs, buy_ys, sell_xs, sell_ys):
		self.buy_xs = buy_xs
		self.buy_ys = buy_ys
		self.sell_xs = sell_xs
		self.sell_ys = sell_ys

class Price_Trades():
	def __init__(self, buy_xs, buy_ys, sell_xs, sell_ys):
		self.buy_xs = buy_xs
		self.buy_ys = buy_ys
		self.sell_xs = sell_xs
		self.sell_ys = sell_ys


def macd_diff_smooth(df, start=0, end=-1):
	in_trade = False
	window_size = 7
	macd_diff_data = []
	macd_diff_smooth_values = []
	itrades = Indicator_Trades([],[],[],[])
	ptrades = Price_Trades([],[],[],[])
	end = len(df.Close) if end==-1 else end

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
				print("buy:  ", macd_diff_smooth_values[-1]-macd_diff_smooth_values[-2])
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
				print("sell: ", macd_diff_smooth_values[-1]-macd_diff_smooth_values[-2], "\n")

	return ptrades, itrades, macd_diff_smooth_values


def plot_macd_diff_smooth(df, ptrades, itrades, macd_diff_smooth_values, start=0, end=-1):
	end = len(df.Close) if end==-1 else end
	mpl.style.use('seaborn')

	# Plot the price
	fig, axs = plt.subplots(2, sharex=True)
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


def trade_with_macd_diff_smooth(df, start=0, end=-1):
	ptrades, itrades, macd_diff_smooth_values = macd_diff_smooth(df, start, end)
	plot_macd_diff_smooth(df, ptrades, itrades, macd_diff_smooth_values, start, end)
	return ptrades
