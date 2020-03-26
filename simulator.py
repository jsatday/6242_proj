from datetime import datetime
# from kaggle.api.kaggle_api_extended import KaggleApi
from scipy import signal
import csv
import mplcursors
import os
import ta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# Initialize the API
# api = KaggleApi()
# api.authenticate()

class Trades():
	def __init__(self, buy_xs, buy_ys, sell_xs, sell_ys):
		self.buy_xs = buy_xs
		self.buy_ys = buy_ys
		self.sell_xs = sell_xs
		self.sell_ys = sell_ys


def init_stocks_dir():
	try:
		os.mkdir("Stocks")
	except OSError:
		print("Creation of the directory 'Stocks' failed: It might exist already")


def get_ticker_data(ticker):
	ticker_path = "Stocks/"+ticker+".us.txt"
	if os.path.isfile(ticker_path):
		print("%s already exists." % (ticker_path))
	else:
		global api
		api.dataset_download_file("borismarjanovic/price-volume-data-for-all-us-stocks-etfs", ticker_path, path="Stocks/")
		# api.dataset_download_files("borismarjanovic/price-volume-data-for-all-us-stocks-etfs", path="Stocks/")
		print("Download complete: %s.us.txt" % (ticker))


def macd_diff_smooth(df, start=0, end=-1):
	in_trade = False
	window_size = 7
	macd_diff_data = []
	macd_diff_smooth_values = []
	trades = Trades([],[],[],[])
	end = len(df.Close) if end==-1 else end

	for i in range(start,end):
		macd_diff_data.append(df.trend_macd_diff[i])
		
		# Wait for enough data to start smoothing the curve
		if len(macd_diff_data) > window_size:
			macd_diff_smooth_values = signal.savgol_filter(macd_diff_data, window_size, 1)

			# Buy the stock
			if macd_diff_smooth_values[-1]-macd_diff_smooth_values[-2] > 0 and not in_trade:
				in_trade = True
				trades.buy_xs.append(i)
				trades.buy_ys.append(macd_diff_smooth_values[-1])
				continue

			# Sell the stock
			if macd_diff_smooth_values[-1]-macd_diff_smooth_values[-2] <= 0 and in_trade:
				in_trade = False
				trades.sell_xs.append(i)
				trades.sell_ys.append(macd_diff_smooth_values[-1])

	return trades, macd_diff_smooth_values


def plot_macd_diff_smooth(df, trades, macd_diff_smooth_values, start=0, end=-1):
	end = len(df.Close) if end==-1 else end
	mpl.style.use('seaborn')

	# Plot the price
	fig, axs = plt.subplots(2, sharex=True)
	axs[0].plot(df[start:end].Close, label='Stock Price')

	# Plot the buys/sells on the price
	axs[0].plot(trades.buy_xs, [df.Close[i] for i in trades.buy_xs], 'ro', color='green', ms=5)
	axs[0].plot(trades.sell_xs, [df.Close[i] for i in trades.sell_xs], 'ro', color='red', ms=5)

	# Plot the MACDs
	axs[1].plot(df[start:end].trend_macd, label='MACD')
	axs[1].plot(df[start:end].trend_macd_signal, label='MACD Signal')
	axs[1].plot(df[start:end].trend_macd_diff, label='MACD Difference')
	axs[1].plot([i for i in range(start,end)], macd_diff_smooth_values, label='MACD Difference Smooth', color='black')

	# Plot the buys/sells on the MACD diff smooth
	axs[1].plot(trades.buy_xs, trades.buy_ys, 'ro', color='green', ms=5)
	axs[1].plot(trades.sell_xs, trades.sell_ys, 'ro', color='red', ms=5)

	plt.show()


def trade_with_macd_diff(df, start=0, end=-1):
	trades, macd_diff_smooth_values = macd_diff_smooth(df, start, end)
	plot_macd_diff_smooth(df, trades, macd_diff_smooth_values, start, end)


def main():
	init_stocks_dir()

	ticker_list = ["aapl"]

	df_list = []
	for ticker in ticker_list:
		# get_ticker_data("ticker")
		df = pd.read_csv("Stocks/"+ticker+".us.txt",sep=",")
		df = ta.add_all_ta_features(df, "Open", "High", "Low", "Close", "Volume", fillna=True)
		trade_with_macd_diff(df)

if __name__ == "__main__":
	main()
