# at a given timestep, initialize a veOcean account by locking ocean
from typing import *
import numpy as np
import uuid
        
def behavior_lock(run, timestep, supply_circ, locked_supply, minlock, maxlock, growth_rate, max_pct, init_lock_pct = 0.005):
    '''
    logic
    - calculate lock amount according to initial value and growth rate
    - uniform random duration of lock (1 week to 4 years)
    '''
    #lock_amount = min(init_lock_pct*((1+growth_rate*((1-growth_rate_decay)**timestep))**timestep), max_pct)*(supply_circ + locked_supply) - locked_supply
    #lock_amount = min(init_lock_pct/(init_lock_pct + np.exp(-(0.1*timestep))), max_pct)*(supply_circ + locked_supply) - locked_supply
    # select a ranom target percent locked between 0 and max_pct. if the target percent is less than the current percent locked, then locke_amount = 0, else lock_amount = (supply_circ + locked_supply)*target_pct - locked_supply
    target_pct = np.random.uniform(0.0, max_pct)
    if target_pct < locked_supply/(supply_circ + locked_supply):
        lock_amount = 0
        lock_duration = 1
    else:
        lock_amount = (supply_circ + locked_supply)*target_pct - locked_supply
        lock_duration = np.random.randint(minlock, maxlock)
    return lock_amount, lock_duration

# According to logic (at timestep X) set the ve allocation percent for a data asset
def behavior_vote(run, timestep, assets: dict) -> Dict[uuid.UUID, float]:
    '''
    logic:
    - uniform random between 0-100: % of veocean successfully allocated to a ranked data assets
    - uniform random between 0-100 for each ranked asset, then normalize and apply to pct_success
    '''
    new_votes = {}
    pct_success = np.random.uniform(0.0,1.0)
    for asset in assets.keys():
        new_votes[asset] = np.random.uniform(0.0,1.0)
    total_votes = sum(new_votes.values())
    for asset in assets.keys():
        new_votes[asset] = new_votes[asset]/total_votes*pct_success
    return new_votes

def behavior_consume_data(run, timestep, assets, dcv_growth_rate = 0, init_dcv = 1000000):
    '''
    logic:
    - generate aggregate DCV for all assets from initial dcv and growth rate
    - uniform random between 0-100% for each asset, then normalize and apply to total dcv
    '''
    #dcv = init_dcv*(1+dcv_growth_rate)**(0.1*timestep)
    dcv = 50*(init_dcv / (1 + np.exp(-(1/100)*(timestep - 400)))) + init_dcv
    assets_consumed = {}
    for asset in assets.keys():
        assets_consumed[asset] = np.random.uniform(0.0,1.0)
    total_consumed = sum(assets_consumed.values())
    for asset in assets.keys():
        assets_consumed[asset] = assets_consumed[asset]/total_consumed*dcv
    return assets_consumed