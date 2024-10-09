import AgentBasedModel.utils.math as math

from scipy.stats import kendalltau
import statsmodels.api as sm
from statistics import mean
import numpy as np

def arbitrage_count(
        info,
        idx:     int   = None,
        threshold: float = 2,
        access:  int   = 0,
        rolling: int   = 1,
    ):
    """
    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id, defaults to None (all exchanges)
    :parap access: Fundamentalist's number of known dividends, defaults to 0
    :param rolling: MA applied to list, defaults to 1
    """

    # plot 1 exchange
    if idx is not None:
        exchange = info.exchanges[idx]
        m_values = math.rolling(info.prices[idx], rolling)                     # market prices
        f_values = math.rolling(info.fundamental_value(idx, access), rolling)  # fundamental prices
        values = [
            100 * abs(m_values[i] - f_values[i]) / m_values[i]                    # arbitrage opportunity %
            for i in range(len(m_values))
        ]
        iterations = range(rolling - 1, len(values) + rolling - 1)
        return np.sum(np.array(values) > threshold)



def volatility_price_average(
        info,
        idx:     int   = None,
        window:  int   = 20,
    ):
    """
    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id, defaults to None (all exchanges)
    :param window: sample size to calculate std, > 1, defaults to 5
    """
    # plot 1 exchange
    if idx is not None:
        exchange = info.exchanges[idx]
        values = info.price_volatility(idx, window)
        iterations = range(window, len(values) + window)
        return np.array(values).mean()