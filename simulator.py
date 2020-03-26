from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi
from scipy import signal
from zipfile import ZipFile
import csv
import mplcursors
import os
import ta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl


# Initialize the API
api = KaggleApi()
api.authenticate()


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


def init_stocks_dir():
	# Check if stocks exists
	if not os.path.exists("Stocks"):

		# Check if the zip has been downloaded
		if not os.path.exists("price-volume-data-for-all-us-stocks-etfs.zip"):
			print("Downloading database...")
			global api
			api.dataset_download_files("borismarjanovic/price-volume-data-for-all-us-stocks-etfs")
			print("Download complete")

		# Unzip it
		print("Unzipping database...")
		zip = ZipFile("price-volume-data-for-all-us-stocks-etfs.zip")
		for file in zip.namelist():
			if file.startswith('Stocks/'):
				zip.extract(file)
		print("Unzip complete")


# Currently unused
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
	itrades = Indicator_Trades([],[],[],[])
	ptrades = Price_Trades([],[],[],[])
	end = len(df.Close) if end==-1 else end

	for i in range(start,end):
		macd_diff_data.append(df.trend_macd_diff[i])
		
		# Wait for enough data to start smoothing the curve
		if len(macd_diff_data) > window_size:
			macd_diff_smooth_values = signal.savgol_filter(macd_diff_data, window_size, 1)

			# Buy the stock
			if macd_diff_smooth_values[-1]-macd_diff_smooth_values[-2] > 0 and not in_trade:
				in_trade = True
				itrades.buy_xs.append(i)
				itrades.buy_ys.append(macd_diff_smooth_values[-1])
				ptrades.buy_xs.append(i)
				ptrades.buy_ys.append(df.Close[i])
				continue

			# Sell the stock
			if macd_diff_smooth_values[-1]-macd_diff_smooth_values[-2] <= 0 and in_trade:
				in_trade = False
				itrades.sell_xs.append(i)
				itrades.sell_ys.append(macd_diff_smooth_values[-1])
				ptrades.sell_xs.append(i)
				ptrades.sell_ys.append(df.Close[i])

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


def trade_with_macd_diff(df, start=0, end=-1):
	ptrades, itrades, macd_diff_smooth_values = macd_diff_smooth(df, start, end)
	plot_macd_diff_smooth(df, ptrades, itrades, macd_diff_smooth_values, start, end)
	return ptrades


def trade_totals(df, ptrades):
	total = 0
	for i in range(len(ptrades.sell_ys)):
		total += (ptrades.sell_ys[i]-ptrades.buy_ys[i])
	print("Total profit:", round(total, 2))


def main():
	init_stocks_dir()

	ticker_list = ["aapl"]

	df_list = []
	for ticker in ticker_list:
		# get_ticker_data("ticker")
		df = pd.read_csv("Stocks/"+ticker+".us.txt",sep=",")
		df = ta.add_all_ta_features(df, "Open", "High", "Low", "Close", "Volume", fillna=True)
		ptrades = trade_with_macd_diff(df, 5500, 6000)
		trade_totals(df, ptrades)
		plt.show()


if __name__ == "__main__":
	main()
