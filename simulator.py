from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi
import csv
import os

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

for day in data_stream:
	print("Date: %s    Open: %f    High: %f    Low: %f    Close: %f    Volume: %d    OpenInt: %d" %
	(day.date.strftime("%Y-%m-%d"), day.start, day.high, day.low, day.close, day.volume, day.open_int))
