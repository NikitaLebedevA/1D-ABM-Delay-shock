from AgentBasedModel import *
from AgentBasedModel.extra import *
from AgentBasedModel.visualization import (
    plot_price,
    plot_price_fundamental,
    plot_volatility_price,
    plot_arbitrage,
    plot_cash,
    arbitrage_count,
    volatility_price_average
)
from AgentBasedModel.extra.events import InformationDelayShock, MarketPriceShock
from random import randint
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from tqdm import tqdm

# Define parameters
risk_free_rate = 1e-3
price = 100
dividend = price * risk_free_rate

agents_list = [0, 100]
num_marketmakers_list = [0, 10]

def generate_scenarios(num_random, num_fundumentalist, num_chartists):
    scenarios = [
        {
            'description': 'No events',
            'events': []
        },
        {
            'description': 'Delay - Random',
            'events': [InformationDelayShock(0, 150, 20, 0, num_random-1), 
                       InformationDelayShock(0, 250, 0, 0, num_random-1)]
        },
        {
            'description': 'Delay - Fundamentalist',
            'events': [InformationDelayShock(0, 150, 20, num_random, num_fundumentalist+num_random-1), 
                       InformationDelayShock(0, 250, 0, num_random, num_fundumentalist+num_random-1)],
        },
        {
            'description': 'Delay - Half Fundamentalist',
            'events': [InformationDelayShock(0, 150, 20, num_random, num_fundumentalist+num_random//2-1), 
                       InformationDelayShock(0, 250, 0, num_random, num_fundumentalist+num_random//2-1)],
        },
        {
            'description': 'Delay - Chartist2D',
            'events': [InformationDelayShock(0, 150, 20, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists-1), 
                       InformationDelayShock(0, 250, 0, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists-1)],
        },
        {
            'description': 'Delay - Half Chartist2D',
            'events': [InformationDelayShock(0, 150, 20, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists//2-1), 
                       InformationDelayShock(0, 250, 0, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists//2-1)],
        },  
        {
            'description': 'Delay - all',
            'events': [InformationDelayShock(0, 150, 20, 0, num_fundumentalist+num_random+num_chartists), 
                       InformationDelayShock(0, 250, 0, 0, num_fundumentalist+num_random+num_chartists)],
        },
        {
            'description': 'Price shock only',
            'events': [MarketPriceShock(0, 200, -10)],
        },
        {
            'description': 'Both - Random',
            'events': [
                MarketPriceShock(0, 200, -10),
                InformationDelayShock(0, 150, 20, 0, num_random-1), 
                InformationDelayShock(0, 250, 0, 0, num_random-1)
            ],
        },
        {
            'description': 'Both - Fundamentalist',
            'events': [
                MarketPriceShock(0, 200, -10),
                InformationDelayShock(0, 150, 20, num_random, num_fundumentalist+num_random-1), 
                InformationDelayShock(0, 250, 0, num_random, num_fundumentalist+num_random-1)
                ],
        },
        {
            'description': 'Both - Half Fundamentalist',
            'events': [
                MarketPriceShock(0, 200, -20),
                InformationDelayShock(0, 150, 20, num_random, num_fundumentalist+num_random//2-1), 
                InformationDelayShock(0, 250, 0, num_random, num_fundumentalist+num_random//2-1)
            ],
        },
        {
            'description': 'Both - Chartist2D',
            'events': [
                MarketPriceShock(0, 200, -10),
                InformationDelayShock(0, 150, 20, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists-1), 
                InformationDelayShock(0, 250, 0, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists-1)
            ],
        },
        {
            'description': 'Both - Half Chartist2D',
            'events': [
                MarketPriceShock(0, 200, -10),
                InformationDelayShock(0, 150, 20, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists//2-1), 
                InformationDelayShock(0, 250, 0, num_fundumentalist+num_random, num_fundumentalist+num_random+num_chartists//2-1)
            ],
        },
        {
            'description': 'Both - all',
            'events': [
                MarketPriceShock(0, 200, -10),
                InformationDelayShock(0, 150, 20, 0, num_fundumentalist+num_random+num_chartists), 
                InformationDelayShock(0, 250, 0, 0, num_fundumentalist+num_random+num_chartists)
            ],
        }
    ]
    return scenarios

# Function to run simulation and collect states
def run_simulation(events,
                   risk_free_rate, 
                   price, 
                   dividend,
                   num_random, 
                   num_fundumentalist, 
                   num_chartists, 
                   num_marketmakers,
                   num_runs=10):
    
    states_sequences = []
    time_to_recovery = []
    volatility_price_average_list = []
        
    for run in range(num_runs):                  
        try:
            # Initialize assets, exchanges, and traders
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
            states_sequences.append(general_states(info, 0))
            time_to_recovery.append(arbitrage_count(info, 0))
            volatility_price_average_list.append(volatility_price_average(info, 0))
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    return states_sequences, time_to_recovery, volatility_price_average_list

results = []
stats_list = []

# Run simulations for each scenario
for num_marketmakers in num_marketmakers_list:
    print("main iteration")
    print(" ")
    for num_random in agents_list:
        for num_fundumentalist in agents_list:
            for num_chartists in agents_list:
                if num_marketmakers+num_random+num_fundumentalist+num_chartists > 50:
                    scenarios = generate_scenarios(num_random, num_fundumentalist, num_chartists)
                    for scenario in tqdm(scenarios):
                        states_sequences = []
                        arbitrage_list = []
                        volatility_list = []
                        
                        states_sequences, time_to_recovery, volatility_list = run_simulation(
                            scenario['events'], 
                            risk_free_rate, price, dividend, 
                            num_random, num_fundumentalist, num_chartists, num_marketmakers,
                            num_runs=20)
                        results.append({
                            'Main scenario': scenario['description'],
                            'Num agents': f"random {num_random}// fundamentalists {num_fundumentalist}// chartists {num_chartists} // marketmakers {num_marketmakers}",
                            'scenario': f"{scenario['description']}// random {num_random}// fundamentalists {num_fundumentalist}// chartists {num_chartists} // marketmakers {num_marketmakers}",
                            'states_sequences': (states_sequences)})
                        stats_list.append({
                            'scenario': f"{scenario['description']}// random {num_random}// fundamentalists {num_fundumentalist}// chartists {num_chartists} // marketmakers {num_marketmakers}",
                            'time_to_recovery': [np.array(time_to_recovery).mean()],
                            'volatility': [np.array(volatility_list).mean()]})


# Updated save_to_excel function to include state mappings
def save_to_excel(results, stats_list, ks_results, state_mappings, filename='simulation_results.xlsx'):
    with pd.ExcelWriter(filename) as writer:
        k = 0
        for result in results:
            df = pd.DataFrame(result['states_sequences'])
            # Flatten the list of lists into a DataFrame with one column per run
            df = df.apply(pd.Series).transpose()
            # Rename columns with scenario description and run number
            df.columns = [f"{result['scenario']}" for i in range(df.shape[1])]
            df.to_excel(writer, sheet_name='Res', index=False, startcol=k)
            k += 1

        ks_df = pd.DataFrame(ks_results, columns=['Scenario', 'P-value', 'Similar to', 'Comparison'])
        ks_df.to_excel(writer, sheet_name='KS results', index=False)

        for scenario, mapping in state_mappings.items():
            mapping_df = pd.DataFrame(list(mapping.items()), columns=['State', 'Index'])
            mapping_df.to_excel(writer, sheet_name=f"{scenario} SM", index=False)

        # Saving time_to_recovery data
        k = 0
        for stat in stats_list:
            df = pd.DataFrame(stat['time_to_recovery'])
            # Flatten the list of lists into a DataFrame with one column per run
            df = df.apply(pd.Series).transpose()
            # Rename columns with scenario description and run number
            df.columns = [f"{stat['scenario']}" for i in range(df.shape[1])]
            df.to_excel(writer, sheet_name='time_to_recovery', index=False, startcol=k)
            k += 1
        
        # Saving volatility data
        k = 0
        for stat in stats_list:
            df = pd.DataFrame(stat['volatility'])
            # Flatten the list of lists into a DataFrame with one column per run
            df = df.apply(pd.Series).transpose()
            # Rename columns with scenario description and run number
            df.columns = [f"{stat['scenario']}" for i in range(df.shape[1])]
            df.to_excel(writer, sheet_name='volatility', index=False, startcol=k)
            k += 1


# Function to perform Kolmogorov-Smirnov test
def ks_test(sample1, sample2):
    stat, p_value = ks_2samp(sample1, sample2)
    return p_value

# Combining all runs into one sample per scenario
samples = {
    result['scenario']: {
        'states': [state for run in result['states_sequences'] for state in run],
        'Main scenario': result['Main scenario'],
        'Num agents': result['Num agents']
    }
    for result in results}

ks_results = []

# Функция для создания выборки с заданным сценарием и количеством агентов
def create_sample_with_agents(samples, target_scenario, num_agents):
    for scenario, sample in samples.items():
        if sample['Main scenario'] == target_scenario and sample['Num agents'] == num_agents:
            return sample
    return None

# Performing KS tests
for scenario_key, sample in samples.items():
    num_agents = sample['Num agents']
    
        price_shock_sample = create_sample_with_agents(samples, 'Price shock only', num_agents)
    no_events_sample = create_sample_with_agents(samples, 'No events', num_agents)
    
    if price_shock_sample is not None:
        p_value = ks_test(sample['states'], price_shock_sample['states'])
        similar_to = 'Price shock only' if p_value > 0.05 else 'Different'
        ks_results.append((scenario_key, p_value, similar_to, 'Price shock only'))

    if no_events_sample is not None:
        p_value = ks_test(sample['states'], no_events_sample['states'])
        similar_to = 'No events' if p_value > 0.05 else 'Different'
        ks_results.append((scenario_key, p_value, similar_to, 'No events'))

# Saving results to Excel
save_to_excel(results, stats_list, ks_results, {}, filename = 'simulation_results_3nd_run.xlsx')

print('___________')

# Displaying scenarios that produce similar distributions
print("Scenarios with similar distributions to their reference samples:")
for scenario, p_value, similar_to, comparison in ks_results:
    if similar_to != 'Different':
        print(f"{scenario} is similar to {similar_to}")

