from nsetools import Nse
from phi.agent import Agent
from phi.tools import Tool

class NseIndiaTool(Tool):
    def __init__(self):
        self.nse = Nse()

    def get_stock_quote(self, symbol):
        return self.nse.get_quote(symbol)

    def get_stock_list(self):
        return nse.get_stock_codes()
    
    def get_stock_info(self, symbol):
        return self.nse.get_stock_info(symbol)
    
    def get_stock_fno_lot_size(self, symbol):
        return self.nse.get_fno_lot_sizes(symbol)
    
    def get_stock_fno_margin(self, symbol):
        return self.nse.get_fno_margin(symbol)
    
