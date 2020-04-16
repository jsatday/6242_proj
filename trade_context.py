class trade_context():
	def __init__(self):
		self.buy_times = []
		self.buy_prices = []
		self.buy_inds = []
		self.sell_times = []
		self.sell_prices = []
		self.sell_inds = []
		self.pos_size_list = []
		self.price_diff_cur = 0
		self.price_diff_high = 0
		self.in_trade = False
		self.trade_value = 100

def buy_stock(t_ctx, time, price, indicator=None):
	t_ctx.in_trade = True
	t_ctx.buy_times.append(time)
	t_ctx.buy_prices.append(price)
	t_ctx.pos_size_list.append(t_ctx.trade_value/price)
	if indicator != None:
		t_ctx.buy_inds.append(indicator)

def sell_stock(t_ctx, time, price, indicator=None):
	t_ctx.in_trade = False
	t_ctx.price_diff_cur = 0
	t_ctx.price_diff_high = 0
	t_ctx.sell_times.append(time)
	t_ctx.sell_prices.append(price)
	t_ctx.pos_size_list.append(t_ctx.trade_value/price)
	if indicator != None:
		t_ctx.sell_inds.append(indicator)
