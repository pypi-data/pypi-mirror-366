from finlab.market import Market
from finlab import data
import datetime
import pandas as pd

class USMarket(Market):

    @staticmethod
    def get_freq():
        return '1d'

    @staticmethod
    def get_name():
        return 'us_stock'

    @staticmethod
    def get_benchmark():
        return data.get('world_index:adj_close')['^GSPC']

    @staticmethod
    def get_asset_id_to_name():
        categories = data.get('us_tickers')
        stock_names = dict(
            zip(categories['stock_id'], categories['name']))
        return stock_names

    @staticmethod
    def get_price(trade_at_price, adj=True):
        if isinstance(trade_at_price, pd.Series):
            return trade_at_price.to_frame()

        if isinstance(trade_at_price, pd.DataFrame):
            return trade_at_price

        if isinstance(trade_at_price, str):
            if trade_at_price == 'volume':
                return data.get('us_price:volume')

            if adj:
                table_name = 'us_price:adj_'
                price_name = trade_at_price
            else:
                table_name = 'us_price:'
                price_name = trade_at_price

            price = data.get(f'{table_name}{price_name}')
            return price

        raise ValueError('trade_at_price is not allowed. Accepted types are pd.DataFrame, pd.Series, and str.')
    

    def market_close_at_timestamp(self, timestamp=None):

        if timestamp is None:
            timestamp = self.get_price('close').index[-1]

        # check if timestamp is localized, if not, localize it to US/Eastern
        if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
            timestamp = timestamp.tz_localize('US/Eastern')

        # get market close time
        market_close = pd.Timestamp(timestamp.date()) + pd.Timedelta('16:00:00')
        return market_close.tz_localize('US/Eastern')

    @staticmethod    
    def tzinfo():
        return datetime.timezone(datetime.timedelta(hours=-4))
