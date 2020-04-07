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


def macd_cross_smooth(df, start=0, end=-1):
	in_trade = False
	window_size = 3
	macd = []
	macd_smooth = []
	itrades = Indicator_Trades([],[],[],[])
	ptrades = Price_Trades([],[],[],[])
	end = len(df.Close) if end==-1 else end

	for i in range(start,end):
		macd.append(df.trend_macd_diff[i])

		# Wait for enough data to start smoothing the curve
		if len(macd) > window_size:
			macd_smooth = signal.savgol_filter(macd, window_size, 1)

			# Buy the stock
			if (macd_smooth[-1] > df.trend_macd_signal[i] and
				not in_trade):

				in_trade = True
				itrades.buy_xs.append(i)
				itrades.buy_ys.append(macd_smooth[-1])
				ptrades.buy_xs.append(i)
				ptrades.buy_ys.append(df.Close[i])
				continue

			# Sell the stock
			if (macd_smooth[-1] < df.trend_macd_signal[i] and
				in_trade):

				in_trade = False
				itrades.sell_xs.append(i)
				itrades.sell_ys.append(macd_smooth[-1])
				ptrades.sell_xs.append(i)
				ptrades.sell_ys.append(df.Close[i])
				
	return ptrades, itrades, macd_smooth


def plot_macd_cross_smooth(df, ptrades, itrades, macd_smooth, start=0, end=-1):
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
	axs[1].plot([i for i in range(start,end)], macd_smooth, label='MACD Smooth', color='black')
	
	# Plot the buys/sells on the MACD
	axs[1].plot(itrades.buy_xs, itrades.buy_ys, 'ro', color='green', ms=5)
	axs[1].plot(itrades.sell_xs, itrades.sell_ys, 'ro', color='red', ms=5)


def trade_with_macd_cross_smooth(df, start=0, end=-1):
	ptrades, itrades, macd_smooth = macd_cross_smooth(df, start, end)
	plot_macd_cross_smooth(df, ptrades, itrades, macd_smooth, start, end)
	return ptrades
