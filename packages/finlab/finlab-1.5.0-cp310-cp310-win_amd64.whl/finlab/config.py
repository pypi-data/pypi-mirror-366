from finlab.market import Market

def get_default_market():
    from finlab.markets.tw import TWMarket
    return TWMarket()

_market = None

def set_market(market:Market):

    """
    Set the stock market for FinLab machine learning model to generate features and labels.

    Args:
        market (Market): A Market object representing the market.
    """

    global _market

    if isinstance(market, type):
        _market = market()
    else:
        _market = market

def get_market():
    global _market
    if _market is None:
        _market = get_default_market()
    return _market

def reset_market():

    """
    Reset the stock market for FinLab machine learning model to the default market, TWMarket.
    """

    global _market
    _market = get_default_market()
