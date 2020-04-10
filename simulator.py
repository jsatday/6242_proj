from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi
from scipy import signal
from trade_context import trade_context
from zipfile import ZipFile
import argparse
import csv
import mplcursors
import os
import ta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
import wget

import macd_diff_smooth as mds
import macd_cross as mc
import macd_cross_slope as mcs
import rsi


# warnings.filterwarnings("ignore")


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


def trade_totals(df, t_ctx):
	total_profit = 0
	total_gain = 0
	total_loss = 0
	sum_perc_gain = 0
	sum_perc_loss = 0
	win = 0
	loss = 0
	print_each = 0

	for i in range(len(t_ctx.sell_prices)):
		gain = t_ctx.sell_prices[i]-t_ctx.buy_prices[i]
		total_profit += gain

		if gain > 0:
			total_gain += gain
			win += 1
			sum_perc_gain += gain/t_ctx.buy_prices[i]
		else:
			total_loss += gain
			loss += 1
			sum_perc_loss += abs(gain)/t_ctx.buy_prices[i]

	accuracy = win/(win+loss) if loss != 0 else 1
	avg_percent_loss = sum_perc_loss/loss*100 if loss != 0 else 0

	if print_each == 1:
		print("Total profit:   $%0.2f" % (round(total_profit, 2)))
		print("Win/Loss:        %d/%d" % (win, loss if loss != 0 else 0))
		print("Accuracy:        %0.2f%%\n" % (round(accuracy*100, 2)))
		print("Total Gain:     $%0.2f" % (round(total_gain, 2)))
		print("Avg Gain:       $%0.2f" % (round(total_gain, 2)/win))
		print("Avg Perc Gain:   %0.2f%%\n" % (round(sum_perc_gain/win*100, 2)))
		print("Total Loss:    -$%0.2f" % (abs(round(total_loss, 2))))
		print("Avg Loss:      -$%0.2f" % (abs(round(total_loss, 2)/win)))
		print("Avg Perc Loss:   %0.2f%%\n" % (round(avg_percent_loss, 2)))
	return (accuracy,(sum_perc_gain/win))


def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("model", action="store", nargs="+", help="Use a model (or multiple models): \n" \
						"    0: MACD Crossover\n" \
						"    1: MACD Difference Smoothed\n" \
						"    2: MACD slope\n" \
						"	 3: RSI")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-t", action="store", dest="tickers", nargs="+", help="Test a ticker (or multiple)")
	group.add_argument("-s", action="store", dest="sector", help="Test a sector:\n" \
						"    Industrials, Health Care, Information Technology, Consumer Discretionary,\n" \
						"    Utilities, Financials, Materials, Real Estate, Consumer Staples,\n" \
						"    Energy, Telecommunication Services\n")
	parser.add_argument("-y", action="store", dest="year", nargs="+", help="Test a year (or year range)")
	parser.add_argument("-p", action="store_true", dest="plot", default=False, help="Plot the chart")

	# Parse the arguments
	try:
		args = parser.parse_args()
	except TypeError:
		parser.parse_args(["-h"])
		exit(0)

	# There can only be one year or a range of years
	if args.year:
		if len(args.year) > 2:
			print("Error: Only one year or a range of years (two years) is allowed")
			parser.parse_args(["-h"])
			exit(0)

	# Validate that model is a number
	model_nums = []
	try:
		for m in args.model:
			model_nums.append(int(m))
	except:
		print("Error: Enter a valid number")
		exit(0)

	# Populate the list of tickers
	ticker_list = []
	if args.sector:
		ticker_list_caps = []
		cons = pd.read_csv("constituents.csv")
		for ind in cons.index:
			if cons['Sector'][ind] == args.sector:
				ticker_list_caps.append(cons['Symbol'][ind])
		for x in ticker_list_caps:
			ticker_list.append(x.lower())
	else:
		for x in args.tickers:
			ticker_list.append(x)

	# Initialize the Stocks directory
	init_stocks_dir()

	#
	# Run the simulation
	#
	accuracy_total = []
	percentage_gain_total = []

	for ticker in ticker_list:

		# Import the ticker data
		df = pd.read_csv("Stocks/"+ticker+".us.txt",sep=",")
		df = ta.add_all_ta_features(df, "Open", "High", "Low", "Close", "Volume", fillna=True)

		# Pick a model
		t_ctx = 0
		for model_num in model_nums:
			if model_num == 0:
				print("========== MACD Crossover: %s ==========\n" % ticker)
				# t_ctx = mc.trade_with_macd_cross(df, start=5500, end=6000, plot=args.plot)
				t_ctx = mc.trade_with_macd_cross(df, plot=args.plot)

			elif model_num == 1:
				print("========== MACD Difference Smoothed: %s ==========\n" % ticker)
				# t_ctx = mds.trade_with_macd_diff_smooth(df, start=5500, end=6000, plot=args.plot)
				t_ctx = mds.trade_with_macd_diff_smooth(df, plot=args.plot)

			elif model_num == 2:
				print("========== MACD Crossover Slope: %s ==========\n" % ticker)
				# t_ctx = mcs.trade_with_macd_cross_slope(df, start=5500, end=6000, plot=args.plot)
				t_ctx = mcs.trade_with_macd_cross_slope(df, plot=args.plot)
			elif model_num == 3:
				print("========== RSI: %s ==========\n" % ticker)
				# t_ctx = mcs.trade_with_macd_cross_slope(df, start=5500, end=6000, plot=args.plot)
				t_ctx = rsi.trade_with_rsi(df, plot=args.plot)

			else:
				print("Error: pick a valid model number")

			# Find the totals
			accuracy_ticker = trade_totals(df, t_ctx)
			accuracy_total.append(accuracy_ticker[0])
			percentage_gain_total.append(accuracy_ticker[1])
	

		# Show the plots
		if args.plot:
			plt.show()
	print(np.mean(accuracy_total)*100)
	print(np.mean(percentage_gain_total)*100)

if __name__ == "__main__":
	main()
