import datetime
import pandas as pd
from finlab import data
from finlab.market import Market

class TWMarket(Market):

    @staticmethod
    def get_freq():
        return '1d'

    @staticmethod
    def get_name():
        return 'tw_stock'

    @staticmethod
    def get_benchmark() -> pd.Series:
        return data.get('benchmark_return:發行量加權股價報酬指數').squeeze()

    @staticmethod
    def get_asset_id_to_name():
        categories = data.get('security_categories')
        stock_names = dict(
            zip(categories.reset_index()['stock_id'], categories['name']))

        return stock_names
    
    @staticmethod
    def get_industry():
        categories = data.get('security_categories')
        industry = dict(
            zip(categories.reset_index()['stock_id'], categories['category']))

        return industry

    def get_price(self, trade_at_price, adj=True):
        if isinstance(trade_at_price, pd.Series):
            return trade_at_price.to_frame()

        if isinstance(trade_at_price, pd.DataFrame):
            return trade_at_price

        if isinstance(trade_at_price, str):
            if trade_at_price == 'volume':
                return data.get('price:成交股數')

            if adj:
                table_name = 'etl:adj_'
                price_name = trade_at_price
            else:
                table_name = 'price:'
                price_name = {'open': '開盤價', 'close': '收盤價', 'high': '最高價', 'low': '最低價'}[trade_at_price]

            price = data.get(f'{table_name}{price_name}')
            return price

        raise ValueError('trade_at_price is not allowed (accepted types: pd.DataFrame, pd.Series, str).')

    @staticmethod
    def get_market_value():
        return data.get('etl:market_value')
    

    def market_close_at_timestamp(self, timestamp=None):

        if not isinstance(timestamp, pd.Timestamp) and timestamp is not None:
            timestamp = pd.Timestamp(timestamp).tz_localize('Asia/Taipei')

        if timestamp is None:
            timestamp = pd.Timestamp.now().tz_localize('Asia/Taipei')

        # check if timestamp is localized, if not, localize it to Asia/Taipei
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize('Asia/Taipei')
        
        # get market close time
        market_close = pd.Timestamp(timestamp.date()) + pd.Timedelta('15:00:00')
        return market_close.tz_localize('Asia/Taipei')
    
    @staticmethod
    def tzinfo():
        return datetime.timezone(datetime.timedelta(hours=8))
    
    def get_reference_price(self) -> dict:
        ref_price = data.get('reference_price')
        return ref_price.set_index('stock_id')['收盤價'].to_dict()

    @staticmethod
    def get_odd_lot():
        return 1000
    
    @staticmethod
    def get_board_lot_size():
        return 1000