from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi
from scipy import signal
import csv
import mplcursors
import os
import ta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl


class DailyData():
	def __init__(self, date, start, high, low, close, volume, open_int):
		self.date = date
		self.start = start
		self.high = high
		self.low = low
		self.close = close
		self.volume = volume
		self.open_int = open_int

#
# Change these variables
#

stock_ticker = "aapl"

#
# Import the data into the program
#

# Initialize the API
api = KaggleApi()
api.authenticate()

# Create folder to store data in
try:
	os.mkdir("Stocks")
except OSError:
	print("Creation of the directory 'downloads' failed: It might exist already")

# Get the data from the API
ticker_path = "Stocks/"+stock_ticker+".us.txt"
if os.path.isfile(ticker_path):
	print("%s already exists." % (ticker_path))
else:
	api.dataset_download_file("borismarjanovic/price-volume-data-for-all-us-stocks-etfs", ticker_path, path="Stocks/")
	print("Download compelte: %s.us.txt" % (stock_ticker))

# Import the data from the file
data_stream = []
with open(ticker_path, newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	header = next(reader, None)
	for row in reader:
		data_stream.append(DailyData(datetime.strptime(row[0], "%Y-%m-%d"), 
									 float(row[1]),
									 float(row[2]),
									 float(row[3]),
									 float(row[4]),
									 int(row[5]),
									 int(row[6])))

# Data format 
# 0: Date
# 1: Open
# 2: High
# 3: Low
# 4: Close
# 5: Volume
# 6: OpenInt

#
# Do the analytics and trading here
#

# for day in data_stream:
# 	print("Date: %s    Open: %f    High: %f    Low: %f    Close: %f    Volume: %d    OpenInt: %d" %
# 	(day.date.strftime("%Y-%m-%d"), day.start, day.high, day.low, day.close, day.volume, day.open_int))

df = pd.read_csv(ticker_path,sep=",")
df = ta.add_all_ta_features(df, "Open", "High", "Low", "Close", "Volume", fillna=True)

start = 5500
end = 6001
# end = df.size
macd_diff_data = []
macd_diff_smooth = []
in_trade = False
buy_price = 0
buy_prices = []
buy_xs = []
buy_ys = []
sell_price = 0
sell_prices = []
sell_xs = []
sell_ys = []
trades = []
last = 0
window_size = 7

for i in range(start,end):
	macd_diff_data.append(df.trend_macd_diff[i])
	if len(macd_diff_data) > window_size:
		macd_diff_smooth = signal.savgol_filter(macd_diff_data, window_size, 1)
		if macd_diff_smooth[-1]-macd_diff_smooth[-2] > 0:
			if not in_trade:
				in_trade = True
				buy_price = df.Close[i]
				buy_xs.append(i)
				buy_ys.append(macd_diff_smooth[-1])
				buy_prices.append(buy_price)
				# print(macd_diff_smooth[-1]-macd_diff_smooth[-2])
				# print("buy ", i, "   ", round(buy_price, 2))
				continue

		if macd_diff_smooth[-1]-macd_diff_smooth[-2] <= 0:
			if in_trade:
				in_trade = False
				sell_price = df.Close[i]
				sell_xs.append(i)
				sell_ys.append(macd_diff_smooth[-1])
				sell_prices.append(sell_price)
				# print(macd_diff_smooth[-1]-macd_diff_smooth[-2])
				# print("sell", i, "   ", round(sell_price, 2), "\n")
				trades.append(round(sell_price-buy_price,2))


print(trades)
print(round(sum(trades),2))

mpl.style.use('seaborn')

fig, axs = plt.subplots(2, sharex=True)
axs[0].plot(df[start:end].Close, label='Stock Price')
axs[0].plot(buy_xs, buy_prices, 'ro', color='green')
axs[0].plot(sell_xs, sell_prices, 'ro', color='red')

axs[1].plot(df[start:end].trend_macd, label='MACD')
axs[1].plot(df[start:end].trend_macd_signal, label='MACD Signal')
axs[1].plot(df[start:end].trend_macd_diff, label='MACD Difference')
axs[1].plot([i for i in range(start,end)], macd_diff_smooth, label='MACD Difference Smooth', color='black')

axs[1].plot(buy_xs, buy_ys, 'ro', color='green')
axs[1].plot(sell_xs, sell_ys, 'ro', color='red')

# plt.title('MACD, MACD Signal and MACD Difference')
# plt.legend()
# mplcursors.cursor()

plt.show()
