# at a given timestep, initialize a veOcean account by locking ocean
from typing import *
import numpy as np
import uuid
import scipy

def behavior_lock_1(run, timestep, unlocked_supply, locked_supply, minlock, maxlock, lock_supply_cap, init_lock_pct = 0.03):
    '''
    logic
    - Amount: Linear function initialized at X% locked supply growing to Y% ceiling after Z years
    - Duration: uniform random between 1 week and 4 years
    '''
    lock_amount = ((lock_supply_cap - init_lock_pct) / 800 * timestep + init_lock_pct) * (unlocked_supply + locked_supply) - locked_supply
    lock_duration = np.random.randint(minlock, maxlock)    
    return lock_amount, lock_duration
        
def behavior_lock_2(passive_rewards, fees_rewards, min_accepted_weekly_yield, unlocked_supply, locked_supply, minlock, maxlock):
    '''
    logic
    - Amount: APY Targeting. If Passive APY > minimum justifiable APY, lock the amount that would bring Passive APY=minimum justifiable APY. If not, don't lock anything and let the locked amount decay.
    - Duration: uniform random duration of lock (1 week to 4 years)

    if passive rewards / some amt between 0 and circulating supply > min_apy:
    '''
    if locked_supply == 0: # if nothing is locked, lock the amt that would bring passive_weekly_yield to min_accepted_weekly_yield
        lock_amount = min((passive_rewards + fees_rewards) / (min_accepted_weekly_yield), unlocked_supply)
    else:
        weekly_yield = (passive_rewards + fees_rewards)/locked_supply
        if weekly_yield < min_accepted_weekly_yield: #let locked amount decay which would increase weekly yield
            lock_amount = 0
        else: #lock the amt that brings weekly yield to min_accepted_weekly_yield
            lock_amount = min((passive_rewards + fees_rewards) / (min_accepted_weekly_yield), (unlocked_supply + locked_supply)) - locked_supply
    lock_duration = np.random.randint(minlock, maxlock)
    return lock_amount, lock_duration

def behavior_vote_active_1():
    pct = np.random.uniform(0.0,1.0)
    return pct

def behavior_vote_active_2(timestep, locked_supply, eligible_passive_rewards, eligible_active_rewards, eligible_fee_rewards, min_accepted_weekly_yield, tot_dcv, yield_cap):
    if locked_supply == 0:
        pct = 0
    else:
        passive_weekly_yield = eligible_passive_rewards/locked_supply
        fees_weekly_yield = eligible_fee_rewards/locked_supply
        dcv_ceiling = tot_dcv * 0.01
        distro_ceiling = eligible_active_rewards
        if passive_weekly_yield+fees_weekly_yield < min_accepted_weekly_yield:

            #print(f'Optimizing! timestep: {timestep}, p_apy: {passive_apy}, f_apy: {fees_apy}, locked_supply: {locked_supply}, p_rewards: {p_rewards}, f_rewards: {f_rewards}')
            def cost(active_supply):
                return -active_supply
            def constraint1(active_supply, m = min_accepted_weekly_yield, p = passive_weekly_yield, f = fees_weekly_yield, c = yield_cap, l = locked_supply): #ineq
                return m - p - f - c*active_supply/l
            def constraint2(active_supply, l = locked_supply):
                return l - active_supply
            def constraint3(active_supply, d = dcv_ceiling, c = yield_cap):
                return d / c - active_supply
            def constraint4(active_supply, di = distro_ceiling, c = yield_cap):
                return di / c - active_supply
            
            all_constraints = [{'type':'ineq', 'fun': constraint1}
                               , {'type':'ineq', 'fun': constraint2}
                               , {'type':'ineq', 'fun': constraint3}
                               , {'type':'ineq', 'fun': constraint4}]

            output = scipy.optimize.minimize(cost, 0, constraints=all_constraints)
            active_supply = output.x[0]
            active_supply

            pct = active_supply / locked_supply
        else:
            #print(f'Did not optimize... timestep: {timestep}, p_apy: {passive_apy}, f_apy: {fees_apy}, locked_supply: {locked_supply}, p_rewards: {p_rewards}, f_rewards: {f_rewards}')
            pct = 0
    return pct

def behavior_vote_strategy_1(run, active_pct, assets: dict) -> Dict[uuid.UUID, float]:
    '''
    logic:
    - uniform random between 0-100: % of veocean successfully allocated to a ranked data assets
    - uniform random between 0-100 for each ranked asset, then normalize and apply to active_pct
    '''
    new_votes = {}
    for asset in assets.keys():
        new_votes[asset] = np.random.uniform(0.0,1.0)
    total_votes = sum(new_votes.values())
    for asset in assets.keys():
        new_votes[asset] = new_votes[asset]/total_votes*active_pct
    return new_votes

def behavior_vote_strategy_2(run, active_pct, assets: dict, max_assets_ranked) -> Dict[uuid.UUID, float]:
    '''
    logic:
    - perfect allocation
    - active veOcean is allocated to the ranked assets according to the same logrithmic distribution that is used in the rewards function.
    '''
    data_assets = np.array([])
    dcv_rewards_period = np.array([])
    for asset in assets:
        # to make ranking process simple, we need two identical arrays: one with data_assets, one with the corresponding DCV
        data_assets = np.append(data_assets, asset)
        dcv_rewards_period = np.append(dcv_rewards_period, assets[asset].dataconsumevolume)
    ranks = scipy.stats.rankdata(-1 * dcv_rewards_period, method='min')
    
    # Rank j - pct_j
    allocations = np.zeros_like(ranks)
    allocations = allocations.astype(float)
    top_indicies = np.where(ranks <= max_assets_ranked)
    logranks = np.log10(ranks)
    allocations[top_indicies] = max(logranks[top_indicies]) - logranks[top_indicies] + np.log10(1.5)
    allocations_normalized = allocations / np.sum(allocations) * active_pct

    new_votes = {}
    for asset in assets.keys():
        new_votes[asset] = allocations_normalized[data_assets == asset]
    return new_votes

def behavior_consume_amt_1(timestep, init_dcv = 50000):
    #logic: generate aggregate DCV for all assets from initial dcv
    dcv = (5e7 / (1 + np.exp(-(1/100)*(timestep - 200)))) - ((5e7 / (1 + np.exp(-(1/100)*(0 - 200)))) - init_dcv)
    return dcv
def behavior_consume_amt_2(timestep, init_dcv = 50000):
    #logic: generate aggregate DCV for all assets from initial dcv
    dcv = (5e7 / (1 + np.exp(-(1/100)*(timestep - 400)))) - ((5e7 / (1 + np.exp(-(1/100)*(0 - 400)))) - init_dcv)
    return dcv
def behavior_consume_amt_3(timestep, init_dcv = 50000):
    #logic: generate aggregate DCV for all assets from initial dcv
    dcv = (5e7 / (1 + np.exp(-(1/100)*(timestep - 600)))) - ((5e7 / (1 + np.exp(-(1/100)*(0 - 600)))) - init_dcv)
    return dcv


def behavior_consume_distr_1(assets, dcv):
    '''
    logic:
    - uniform random between 0-100% for each asset, then normalize and apply to total dcv
    '''
    assets_consumed = {}
    for asset in assets.keys():
        assets_consumed[asset] = np.random.uniform(0.0,1.0)
    total_consumed = sum(assets_consumed.values())
    for asset in assets.keys():
        assets_consumed[asset] = assets_consumed[asset]/total_consumed*dcv
    return assets_consumed

def behavior_consume_distr_2(assets, dcv):
    '''
    logic:
    - perfect allocation. DCV is allocated to the ranked assets according to the same logrithmic distribution that is used in the rewards function.
    '''
    ranks = np.arange(1,101,1)
    allocations = np.zeros_like(ranks)
    allocations = allocations.astype(float)
    top_indicies = np.where(ranks > 0)
    logranks = np.log10(ranks)
    allocations[top_indicies] = max(logranks[top_indicies]) - logranks[top_indicies] + np.log10(1.5)
    allocations_normalized = allocations / np.sum(allocations)

    assets_consumed = {}
    i=0
    for asset in assets.keys():
            assets_consumed[asset] = allocations_normalized[i] * dcv
            i += 1
    return assets_consumed