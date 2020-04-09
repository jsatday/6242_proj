class trade_context():
	def __init__(self):
		self.buy_times = []
		self.buy_prices = []
		self.buy_inds = []
		self.sell_times = []
		self.sell_prices = []
		self.sell_inds = []
		self.price_diff_cur = 0
		self.price_diff_high = 0
		self.in_trade = False

def buy_stock(trade_context, time, price, indicator=None):
	trade_context.in_trade = True
	trade_context.buy_times.append(time)
	trade_context.buy_prices.append(price)
	if indicator != None:
		trade_context.buy_inds.append(indicator)

def sell_stock(trade_context, time, price, indicator=None):
	trade_context.in_trade = False
	trade_context.price_diff_cur = 0
	trade_context.price_diff_high = 0
	trade_context.sell_times.append(time)
	trade_context.sell_prices.append(price)
	if indicator != None:
		trade_context.sell_inds.append(indicator)
