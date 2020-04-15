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


def check_valid_date_range(df, s_year, e_year):
	# Check if valid ints
	try:
		s_year = int(s_year)
		e_year = int(e_year)
	except:
		print("Error: year is not a valid int")
		return False

	# Check for valid range
	if e_year < s_year:
		print("Error: end year is less than start year")
		return False

	# Check if stock existed in that range
	if int(df.Date[0][0:4]) <= s_year and int(df.Date[len(df.Date)-1][0:4]) >= e_year:
		return True
	else:
		print("Error: not a valid date range. Try dates beween: %s-%s" % (df.Date[0][0:4], df.Date[len(df.Date)-1][0:4]))
		return False


def export_to_csv(filename, model, avg_total_perc_gain, sector, year):
	with open(filename+".csv", "a", newline="") as f:
		writer = csv.writer(f, delimiter=",")
		writer.writerow([model, avg_total_perc_gain, sector, year])


def trade_totals(df, t_ctx, print_each=False):
	total_profit = 0
	total_gain = 0
	total_loss = 0
	sum_perc_gain = 0
	sum_perc_loss = 0
	win = 0
	loss = 0

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

	accuracy = win/(win+loss)                  if loss != 0 else 1
	avg_percent_loss = sum_perc_loss/loss*100  if loss != 0 else 0
	avg_gain = total_gain/win                  if win  != 0 else 0
	avg_percent_gain = sum_perc_gain/win*100   if win  != 0 else 0
	avg_loss = total_loss/win                  if win  != 0 else 0
	avg_total_perc_gain = avg_percent_gain*accuracy-avg_percent_loss*(1-accuracy)

	if print_each:
		print("Avg Total Perc Gain:  %0.2f%%\n" % (round(avg_total_perc_gain, 2)))
		print("Total Profit:        $%0.2f" % (round(total_profit, 2)))
		print("Win/Loss:             %d/%d" % (win, loss if loss != 0 else 0))
		print("Accuracy:             %0.2f%%\n" % (round(accuracy*100, 2)))
		print("Total Gain:          $%0.2f" % (round(total_gain, 2)))
		print("Avg Gain:            $%0.2f" % (round(avg_gain, 2)))
		print("Avg Perc Gain:        %0.2f%%\n" % (round(avg_percent_gain, 2)))
		print("Total Loss:         -$%0.2f" % (abs(round(total_loss, 2))))
		print("Avg Loss:           -$%0.2f" % (abs(round(avg_loss, 2))))
		print("Avg Perc Loss:        %0.2f%%\n" % (round(avg_percent_loss, 2)))

	return avg_total_perc_gain


def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("model", action="store", nargs="+", help="Use a model (or multiple models): \n" \
						"    0: MACD Crossover\n" \
						"    1: MACD Difference Smoothed\n" \
						"    2: MACD slope\n" \
						"	 3: RSI")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-t", action="store", dest="tickers", nargs="+", help="Test a ticker (or multiple).")
	group.add_argument("-s", action="store", dest="sector", help="Test a sector:\n" \
						"    Industrials, HealthCare, InformationTechnology, ConsumerDiscretionary,\n" \
						"    Utilities, Financials, Materials, RealEstate, ConsumerStaples,\n" \
						"    Energy, TelecommunicationServices\n")
	parser.add_argument("-y", action="store", dest="year", nargs="+", help="Test a year (or year range).")
	parser.add_argument("-e", action="store", dest="filename", help="Export results to a file. Will append to existing file.")
	parser.add_argument("-p", action="store_true", dest="plot", default=False, help="Plot the chart.")
	parser.add_argument("-v", action="store_true", dest="verbose", default=False, help="Show the results of each ticker.")

	# Parse the arguments
	try:
		args = parser.parse_args()
	except TypeError:
		parser.parse_args(["-h"])
		exit(0)

	# There can only be one year or a range of years
	s_year = 0
	e_year = 0
	if args.year:
		if len(args.year) > 2:
			print("Error: Only one year or a range of years (two years) is allowed")
			parser.parse_args(["-h"])
			exit(-1)
		s_year = int(args.year[0])
		e_year = int(args.year[-1])

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

	# Initialize results dictionary
	results_dict = {}

	#
	# Run the simulation
	#

	for ticker in ticker_list:

		# Import the ticker data
		try:
			df = pd.read_csv("Stocks/"+ticker+".us.txt",sep=",")
			df = ta.add_all_ta_features(df, "Open", "High", "Low", "Close", "Volume", fillna=True)
			if args.year:
				if not check_valid_date_range(df, args.year[0], args.year[-1]):
					print("Skipping over ticker: %s\n" % ticker.upper())
					continue
		except OSError as e:
			print("%s:" % (ticker), e)
			continue

		# Initialize variables
		t_ctx = 0

		# Make verbosity pretty
		if args.verbose:
			print("==============\n    ", ticker.upper(), "\n==============\n")

		# Pick a model
		for model_num in model_nums:

			if model_num == 0:
				if args.verbose:
					print("========== MACD Crossover: %s ==========\n" % ticker.upper())
				# t_ctx = mc.trade_with_macd_cross(df, start=5500, end=6000, plot=args.plot)
				t_ctx = mc.trade_with_macd_cross(df, plot=args.plot, s_year=s_year, e_year=e_year)

			elif model_num == 1:
				if args.verbose:
					print("========== MACD Difference Smoothed: %s ==========\n" % ticker.upper())
				# t_ctx = mds.trade_with_macd_diff_smooth(df, start=5500, end=6000, plot=args.plot)
				t_ctx = mds.trade_with_macd_diff_smooth(df, plot=args.plot, s_year=s_year, e_year=e_year)

			elif model_num == 2:
				if args.verbose:
					print("========== MACD Crossover Slope: %s ==========\n" % ticker.upper())
				# t_ctx = mcs.trade_with_macd_cross_slope(df, start=5500, end=6000, plot=args.plot)
				t_ctx = mcs.trade_with_macd_cross_slope(df, plot=args.plot, s_year=s_year, e_year=e_year)

			elif model_num == 3:
				if args.verbose:
					print("========== RSI: %s ==========\n" % ticker.upper())
				# t_ctx = mcs.trade_with_macd_cross_slope(df, start=5500, end=6000, plot=args.plot)
				t_ctx = rsi.trade_with_rsi(df, plot=args.plot, s_year=s_year, e_year=e_year)

			else:
				print("Error: pick a valid model number")
				continue

			# Find the totals
			avg_total_perc_gain = trade_totals(df, t_ctx, args.verbose)

			# Add results to dictionary
			if args.filename:
				if model_num in results_dict.keys():
					results_dict[model_num].append(avg_total_perc_gain)
				else:
					results_dict[model_num] = [avg_total_perc_gain]

		# Show the plots
		if args.plot:
			plt.show()

	# Export results to a csv
	if args.filename:
		export_sector = args.sector if args.sector else "None"
		export_year = args.year[0] if args.year else "None"
		for model_num in results_dict.keys():
			export_to_csv(args.filename, model_num, round(sum(results_dict[model_num])/len(results_dict[model_num]),2), export_sector, export_year)


if __name__ == "__main__":
	main()
