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

import macd_diff_smooth as mds
import macd_cross as mc
import macd_cross_smooth as mcs

# Initialize the API
api = KaggleApi()
api.authenticate()


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


def trade_totals(df, ptrades):
	total_profit = 0
	total_gain = 0
	total_loss = 0
	sum_perc_gain = 0
	sum_perc_loss = 0
	win = 0
	loss = 0

	for i in range(len(ptrades.sell_ys)):
		gain = ptrades.sell_ys[i]-ptrades.buy_ys[i]
		total_profit += gain

		if gain > 0:
			total_gain += gain
			win += 1
			sum_perc_gain += gain/ptrades.buy_ys[i]
		else:
			total_loss += gain
			loss += 1
			sum_perc_loss += abs(gain)/ptrades.buy_ys[i]

	accuracy = win/(win+loss)

	print("Total profit:   $%0.2f" % (round(total_profit, 2)))
	print("Win/Loss:        %d/%d" % (win, loss))
	print("Accuracy:        %0.2f%%\n" % (round(accuracy*100, 2)))
	print("Total Gain:     $%0.2f" % (round(total_gain, 2)))
	print("Avg Gain:       $%0.2f" % (round(total_gain, 2)/win))
	print("Avg Perc Gain:   %0.2f%%\n" % (round(sum_perc_gain/win*100, 2)))
	print("Total Loss:    -$%0.2f" % (abs(round(total_loss, 2))))
	print("Avg Loss:      -$%0.2f" % (abs(round(total_loss, 2)/win)))
	print("Avg Perc Loss:   %0.2f%%" % (round(sum_perc_loss/loss*100, 2)))


def main():
	init_stocks_dir()

	ticker_list = ["ba"]

	df_list = []
	for ticker in ticker_list:
		# get_ticker_data("ticker")
		df = pd.read_csv("Stocks/"+ticker+".us.txt",sep=",")
		df = ta.add_all_ta_features(df, "Open", "High", "Low", "Close", "Volume", fillna=True)
		# for val in df:
		# 	print(val)
		# ptrades = mds.trade_with_macd_diff_smooth(df, 5500, 6000)
		# ptrades = mc.trade_with_macd_cross(df, 5500, 6000)
		ptrades = mcs.trade_with_macd_cross_smooth(df, 5500, 6000)
		trade_totals(df, ptrades)
		plt.show()


if __name__ == "__main__":
	main()
