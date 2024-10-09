from AgentBasedModel import *
from AgentBasedModel.extra import *
from AgentBasedModel.visualization import (
    plot_price,
    plot_price_fundamental,
    plot_volatility_price,
    plot_arbitrage,
    plot_liquidity,
    plot_book_stat,
    plot_book
)

from AgentBasedModel.extra.events import InformationDelayShock, MarketPriceShock
from random import randint
import random
import matplotlib.pyplot as plt
import numpy as np

# Define parameters
risk_free_rate = 1e-3
price = 100
dividend = price * risk_free_rate

num_random = 100
num_fundumentalist = 100
num_chartists = 100
num_marketmakers = 10

scenario = {
            # 'description': 'No events',
            # 'events': []
        # },
        # {
        #     'description': 'Delay - Random',
        #     'events': [InformationDelayShock(0, 150, 20, 0, num_random-1), 
        #                InformationDelayShock(0, 250, 0, 0, num_random-1)]
        # },
        # {
            # 'description': 'Delay - Fundamentalist',
            # 'events': [InformationDelayShock(0, 150, 100, num_random, num_fundumentalist+num_random-1), 
            #            InformationDelayShock(0, 250, 0, num_random, num_fundumentalist+num_random-1)],
        # },
        # {
            # 'description': 'Delay - Half Fundamentalist',
            # 'events': [InformationDelayShock(0, 150, 20, num_random, num_fundumentalist+num_random//2-1), 
            #            InformationDelayShock(0, 250, 0, num_random, num_fundumentalist+num_random//2-1)],
        # },
        # {
        #     'description': 'Delay - Chartist2D',
        #     'events': [InformationDelayShock(0, 150, 20, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists-1), 
        #                InformationDelayShock(0, 250, 0, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists-1)],
        # },
        # {
        #     'description': 'Delay - Half Chartist2D',
        #     'events': [InformationDelayShock(0, 150, 20, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists//2-1), 
        #                InformationDelayShock(0, 250, 0, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists//2-1)],
        # },  
        # {
            'description': 'Delay - all',
            'events': [InformationDelayShock(0, 150, 20, 0, num_fundumentalist+num_random+num_chartists), 
                       InformationDelayShock(0, 250, 0, 0, num_fundumentalist+num_random+num_chartists)],
        # },
        # {
            # 'description': 'Price shock only',
            # 'events': [MarketPriceShock(0, 200, -10)],
        # },
        # {
            # 'description': 'Both - Random',
            # 'events': [
            #     MarketPriceShock(0, 200, -10),
            #     InformationDelayShock(0, 150, 20, 0, num_random-1), 
            #     InformationDelayShock(0, 250, 0, 0, num_random-1)
            # ],
        # },
        # {
            # 'description': 'Both - Fundamentalist',
            # 'events': [
            #     MarketPriceShock(0, 200, -10),
            #     InformationDelayShock(0, 150, 20, num_random, num_fundumentalist+num_random-1), 
            #     InformationDelayShock(0, 250, 0, num_random, num_fundumentalist+num_random-1)
            #     ],
        # },
        # {
            # 'description': 'Both - Half Fundamentalist',
            # 'events': [
            #     MarketPriceShock(0, 200, -20),
            #     InformationDelayShock(0, 150, 20, num_random, num_fundumentalist+num_random//2-1), 
            #     InformationDelayShock(0, 250, 0, num_random, num_fundumentalist+num_random//2-1)
            # ],
        # },
        # {
            # 'description': 'Both - Chartist2D',
            # 'events': [
            #     MarketPriceShock(0, 200, -10),
            #     InformationDelayShock(0, 150, 20, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists-1), 
            #     InformationDelayShock(0, 250, 0, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists-1)
            # ],
        # },
        # {
            # 'description': 'Both - Half Chartist2D',
            # 'events': [
            #     MarketPriceShock(0, 200, -10),
            #     InformationDelayShock(0, 150, 20, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists//2-1), 
            #     InformationDelayShock(0, 250, 0, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists//2-1)
            # ],
        # },
        # {
            # 'description': 'Both - all',
            # 'events': [
            #     MarketPriceShock(0, 200, -10),
            #     InformationDelayShock(0, 150, 50, 0, num_fundumentalist+num_random+num_chartists), 
            #     InformationDelayShock(0, 250, 0, 0, num_fundumentalist+num_random+num_chartists)
            # ],
        }

def run_simulation(events,
                   risk_free_rate, 
                   price, 
                   dividend,
                   num_random, 
                   num_fundumentalist, 
                   num_chartists, 
                   num_marketmakers,
                   num_runs=10):
    assets = [Stock(dividend) for _ in range(3)]
    exchanges = [ExchangeAgent(0, assets[0], risk_free_rate) for _ in range(1)]  # single asset
    traders = [
               *[Random(exchanges[0])         for _ in range(num_random)],
               *[Fundamentalist(exchanges[0]) for _ in range(num_fundumentalist)],
               *[Chartist2D(exchanges)        for _ in range(num_chartists)],
               *[MarketMaker2D(exchanges)     for _ in range(num_marketmakers)]]
           
    simulator = Simulator(**{
        'assets': assets,
        'exchanges': exchanges,
        'traders': traders,
        'events': events})
    simulator.simulate(400, silent=True)
    info = simulator.info
    return info

info = run_simulation(scenario['events'], risk_free_rate, price, dividend, num_random, num_fundumentalist,
               num_chartists, num_marketmakers,num_runs=1)


# plot_price_fundamental(info, None, rolling=1)



# print(general_states(info, 0))

# plt.plot(info.price_volatility(0, 20) > np.percentile(info.price_volatility(0, 20)[0:200], 75))
# plt.title("price volatility treshold breaches")

plot_price_fundamental(info, None, rolling=1)

# plot_book_stat(simulator.info, 0)

# plot_volatility_price(info, None)

# plot_arbitrage(info, None)

# plot_book(simulator.info, 0)