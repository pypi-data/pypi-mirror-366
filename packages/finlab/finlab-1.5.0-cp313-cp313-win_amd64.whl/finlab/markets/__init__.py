from finlab.market import Market
from .tw import TWMarket
from .us import USMarket

def get_market_by_name(name:str) -> Market:
    if name.lower() == 'tw_stock':
        return TWMarket()
    if name.lower() == 'us_stock':
        return USMarket()
    raise ValueError('Unknown market name.')