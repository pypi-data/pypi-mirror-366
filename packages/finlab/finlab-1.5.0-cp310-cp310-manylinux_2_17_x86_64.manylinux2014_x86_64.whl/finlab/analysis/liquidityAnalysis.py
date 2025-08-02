import pandas as pd
from finlab import data
from finlab.analysis import Analysis
from finlab.markets.tw import TWMarket


class LiquidityAnalysis(Analysis):

  def __init__(self, required_volume=200000, required_turnover=1000000):
    """分析台股策略流動性風險項目的機率

    !!! note
        參考[VIP限定文章](https://www.finlab.tw/customized_liquidityanalysis/)更了解流動性檢測內容細節。
    Args:
        required_volume (int): 要求進出場時的單日成交股數至少要多少？
        required_turnover (int): 要求進出場時的單日成交金額至少要多少元？避免成交股數夠，但因低價股因素，造成胃納量仍無法符合資金需求。

    Examples:
        ``` py

        # better syntax
        report.run_analysis('LiquidityAnalysis', required_volume=100000)

        # original syntax
        from finlab.analysis.liquidityAnalysis import LiquidityAnalysis
        report.run_analysis(LiquidityAnalysis(required_volume=100000))
        ```
    """

    self._required_volume = required_volume
    self._required_turnover = required_turnover
    self._result = None

  def is_market_supported(self, market):
    return 'TWMarketInfo' in str(market)

  def calculate_trade_info(self, report):

    # calculate trade bar return
    adj_trade_price = report.market.get_trading_price(report.trade_at, adj=True)
    adj_previous_close = report.market.get_trading_price('close', adj=True).shift()

    # calculate money flow
    trade_price = report.market.get_trading_price(report.trade_at, adj=False)
    volume = report.market.get_price('volume', adj=False)

    if volume.shape == adj_previous_close.shape == adj_trade_price.shape == trade_price.shape:
        volume = pd.DataFrame(volume)
        adj_previous_close = pd.DataFrame(adj_previous_close)
        adj_trade_price = pd.DataFrame(adj_trade_price)
        trade_price = pd.DataFrame(trade_price)


    signal_dates = ["entry_sig_date", "exit_sig_date"]
    trading_dates = ["entry_date", "exit_date"]

    # 漲跌幅、成交量、成交金額使用實際交易日期
    ret = [
      ["pct_change", adj_trade_price / adj_previous_close - 1, trading_dates],
      ["turnover", trade_price * volume, trading_dates],
      ["volume", volume, trading_dates]
    ]

    is_tw = isinstance(report.market, TWMarket)

    if is_tw:
        flagged = data.get('etl:is_flagged_stock')
        # 處置股狀態使用信號日期
        ret.append(["類別", flagged, signal_dates])

    return ret

  def analyze(self, report):

    trades = report.get_trades()

    if isinstance(report.market, TWMarket):
      # 漲跌幅限制使用實際交易日期
      entry_pct_range = (trades.entry_date >= '2015-6-1') * 0.03 + 0.07
      exit_pct_range = (trades.exit_date >= '2015-6-1') * 0.03 + 0.07
    else:
      entry_pct_range = 0.1
      exit_pct_range = 0.1

    long_position = trades.position > 0

    # 漲跌幅相關判斷使用實際交易日期
    entry_buy_at_top = long_position & (trades['pct_change@entry_date'] > entry_pct_range * 0.95)
    entry_sell_at_bottom = (~long_position) & (trades['pct_change@entry_date'] < -entry_pct_range * 0.95)

    exit_sell_at_bottom = long_position & (trades['pct_change@exit_date'] < -exit_pct_range * 0.95)
    exit_buy_at_top = (~long_position) & (trades['pct_change@exit_date'] > exit_pct_range * 0.95)
    trade_pct_count = trades['pct_change@entry_date'].notna() & trades['pct_change@exit_date'].notna()

    ret_dict = {
      'buy_high': [entry_buy_at_top.mean(), exit_buy_at_top.mean()],
      'sell_low': [entry_sell_at_bottom.mean(), exit_sell_at_bottom.mean()],
      'low_volume_stocks': [(trades['volume@entry_date'] < self._required_volume).mean(),
                     (trades['volume@exit_date'] < self._required_volume).mean()],
      'low_turnover_stocks': [(trades['turnover@entry_date'] < self._required_turnover).mean(),
                     (trades['turnover@exit_date'] < self._required_turnover).mean()],
    }

    is_tw = isinstance(report.market, TWMarket)
    if is_tw:
        # 處置股相關判斷使用信號日期
        trades['類別@entry_sig_date'] = trades['類別@entry_sig_date'].fillna(0).astype(int)
        trades['類別@exit_sig_date'] = trades['類別@exit_sig_date'].fillna(0).astype(int)
        
        trades['警示股@entry_sig_date'] = (trades['類別@entry_sig_date'] & 0x1) != 0
        trades['處置股@entry_sig_date'] = (trades['類別@entry_sig_date'] & 0x2) != 0
        trades['全額交割股@entry_sig_date'] = (trades['類別@entry_sig_date'] & 0x4) != 0

        trades['警示股@exit_sig_date'] = (trades['類別@exit_sig_date'] & 0x1) != 0
        trades['處置股@exit_sig_date'] = (trades['類別@exit_sig_date'] & 0x2) != 0
        trades['全額交割股@exit_sig_date'] = (trades['類別@exit_sig_date'] & 0x4) != 0

        trades.drop(columns=['類別@entry_sig_date', '類別@exit_sig_date'], inplace=True)

        ret_dict = {**ret_dict, **{
            '警示股': [trades['警示股@entry_sig_date'].mean(), trades['警示股@exit_sig_date'].mean()],
            '處置股': [trades['處置股@entry_sig_date'].mean(), trades['處置股@exit_sig_date'].mean()],
            '全額交割股':[trades['全額交割股@entry_sig_date'].mean(), trades['全額交割股@exit_sig_date'].mean()]
        }}

    self._result = pd.DataFrame(ret_dict)

    self._result.index = ['entry', 'exit']

    return self._result.to_dict()

  def display(self):

    def percentage(v):
        return str(round(v*100, 1)) + '%'

    def make_pretty(styler):
        styler.set_caption("低流動性交易")
        styler.format(percentage)
        styler.background_gradient(axis=None, vmin=0, vmax=0.5, cmap="YlGnBu")
        return styler

    return self._result.style.pipe(make_pretty)
