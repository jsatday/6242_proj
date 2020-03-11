from datetime import datetime
import csv

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
# Import the data into the program
#

# Data format 
# 0: Date
# 1: Open
# 2: High
# 3: Low
# 4: Close
# 5: Volume
# 6: OpenInt

stock_ticker = "aapl.us.txt"
data_file = "/home/g/gt/6242/6242_proj/Stocks/" + stock_ticker
data_stream = []

with open(data_file, newline='') as csvfile:
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

#
# Do the analytics and trading here
#

for day in data_stream:
	print("Date: %s Open: %f High: %f Low: %f Close: %f Volume: %d OpenInt: %d" %
	(day.date.strftime("%Y-%m-%d"), day.start, day.high, day.low, day.close, day.volume, day.open_int))
