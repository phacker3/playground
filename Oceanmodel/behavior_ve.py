# at a given timestep, initialize a veOcean account by locking ocean
from typing import *
import numpy as np
import uuid
import scipy

def behavior_lock_1(run, timestep, unlocked_supply, locked_supply, minlock, maxlock, lock_supply_cap, init_lock_pct = 0.03):
    '''
    logic - Linear Locked Supply Growth
    - Amount: Linear function initialized at X% locked supply growing to Y% ceiling after Z years
    - Duration: uniform random between 1 week and 4 years
    '''
    lock_amount = ((lock_supply_cap - init_lock_pct) / 800 * timestep + init_lock_pct) * (unlocked_supply + locked_supply) - locked_supply
    lock_duration = np.random.randint(minlock, maxlock)    
    return lock_amount, lock_duration
        
def behavior_lock_2(passive_rewards, fees_rewards, min_accepted_weekly_yield, unlocked_supply, locked_supply, minlock, maxlock, lock_supply_cap):
    '''
    logic - "Lazy APY Targeting"
    - Amount: APY Targeting. If Passive APY > minimum justifiable APY, lock the amount that would bring Passive APY=minimum justifiable APY. If not, don't lock anything and let the locked amount decay.
    - Duration: uniform random duration of lock (1 week to 4 years)

    if passive rewards / some amt between 0 and circulating supply > min_apy:
    '''
    if locked_supply == 0: # if nothing is locked, lock the amt that would bring passive_weekly_yield to min_accepted_weekly_yield
        lock_amount = min((passive_rewards + fees_rewards) / (min_accepted_weekly_yield), unlocked_supply * lock_supply_cap)
    else:
        weekly_yield = (passive_rewards + fees_rewards)/locked_supply
        if weekly_yield < min_accepted_weekly_yield: #let locked amount decay which would increase weekly yield
            lock_amount = 0
        else: #lock the amt that brings weekly yield to min_accepted_weekly_yield
            lock_amount = min((passive_rewards + fees_rewards) / (min_accepted_weekly_yield), (unlocked_supply + locked_supply) * lock_supply_cap) - locked_supply
    lock_duration = np.random.randint(minlock, maxlock)
    return lock_amount, lock_duration

def behavior_lock_3(passive_rewards, fees_rewards, active_rewards, min_accepted_weekly_yield, unlocked_supply, locked_supply, minlock, maxlock, lock_supply_cap):
    '''
    logic - "Smart APY Targeting"
    - idea: rather than locked_supply decays to increase passive APY, we consider the potential incremental APY from activating, and potentialy lock more
            if weekly_yield < min_accepted_weekly_yield BUT the previous week's agg_APY was > min_accepted_weekly_yield, then we can actually lock more which would bring agg_weekly_yield in line with min_accepted_weekly_yield
            locked_supply could still decay, but it's to increase agg_APY, not passive_APY
    - Amount: 
    - Duration: x
    '''
    # lock the amt that would bring agg_weekly_yield to min_accepted_weekly_yield
    # maximize locked_supply s.t. agg_weekly_yield >= min_accepted_weekly_yield, where
    # agg_weekly_yield = passive_weekly_yield + passive_fee_yield + active_weekly_yield*active_pct
    # amt = min(eligible_active_rewards / yield_cap, tot_dcv * 0.01 / yield_cap, locked_supply)
    # active_pct = amt / locked_supply
    # active_weekly_yield = min(eligible_active_rewards, tot_dcv*0.01, locked_supply*125%) / amt
    if locked_supply == 0:
        lock_amount = min((passive_rewards + fees_rewards + active_rewards) / min_accepted_weekly_yield, unlocked_supply * lock_supply_cap)
    else:
        agg_weekly_yield = (passive_rewards + fees_rewards + active_rewards)/locked_supply
        if agg_weekly_yield < min_accepted_weekly_yield:
            lock_amount = 0
        else:
            lock_amount = min((passive_rewards + fees_rewards + active_rewards) / min_accepted_weekly_yield, (locked_supply + unlocked_supply) * lock_supply_cap) - locked_supply
    lock_duration = np.random.randint(minlock, maxlock)
    return lock_amount, lock_duration

def behavior_lock_stoch(unlocked_supply, weekly_lock_probability, minlock_amt, maxlock_amt, minlock_dur, maxlock_dur):
    '''
    logic - "stochastic"
    - idea: daily probability of locking/creating a veAccount is X% (so 7 accts are possible per week)
    - Amount: uniform random between 10e3 and 5e6
    - Duration: uniform random 1 week to 4 years
    '''
    lock_amount = np.array([])
    lock_duration = np.array([])

    signal = np.random.uniform(size=(7))
    for i in range(len(signal)):
        if signal[i] < weekly_lock_probability:
            lock_amount = np.append(lock_amount, min(np.random.uniform(minlock_amt, maxlock_amt), unlocked_supply - sum(lock_amount)))
            lock_duration = np.append(lock_duration, np.random.randint(minlock_dur, maxlock_dur))
    return lock_amount, lock_duration

def behavior_vote_active_1():
    # logic: uniform random between
    pct = np.random.uniform(0.0,1.0)
    return pct

def behavior_vote_active_2(timestep, locked_supply, eligible_passive_rewards, eligible_active_rewards, eligible_fee_rewards, min_accepted_weekly_yield, tot_dcv, yield_cap):
    '''
    logic: "lazy APY targeting"
    - only activate as much as is needed to bring the weekly yield to the minimum acceptable yield when passive APY dips below the minimum acceptable yield
    '''
    if locked_supply == 0:
        pct = 0
    else:
        passive_weekly_yield = eligible_passive_rewards/locked_supply
        fees_weekly_yield = eligible_fee_rewards/locked_supply
        dcv_ceiling = tot_dcv * 0.01
        distro_ceiling = eligible_active_rewards
        if passive_weekly_yield+fees_weekly_yield < min_accepted_weekly_yield:
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
            pct = 0
    return pct

def behavior_vote_active_3(timestep, locked_supply, eligible_active_rewards, tot_dcv, yield_cap):
    '''
    logic: "perfect activation"
    - activate as much as is needed to maximize rewards & reach the highest APY (assuming perfect vote allocation & dcv distribution)
    '''
    if locked_supply == 0:
        pct = 0
    else:
        # activate as much is needed to (1) extract all eligible rewards @ yield_cap, or (2) extract all eligble rewards after dcv ceiling @ yield_cap, or (3) active entire locked supply
        amt = min(eligible_active_rewards / yield_cap, tot_dcv * 0.01 / yield_cap, locked_supply)
        pct = amt / locked_supply
    return pct

def behavior_vote_active_stoch(accounts, weekly_vote_success_prob):
    '''
    logic: "stochastic"
    - weekly probability that a ve Account activates it's veOcean balance (i.e votes successfully) = X%
    - depending on which accts are activated, pct = veOcean activated / total veOcean
    '''
    tot_ve_bal = 0
    for acct in accounts:
        tot_ve_bal += accounts[acct].vebalance
    
    if tot_ve_bal == 0:
        pct = 0
    else:
        signal = np.random.uniform(size=len(accounts))
        active_ve_bal = 0
        i = 0
        for acct in accounts:
            if signal[i] < weekly_vote_success_prob:
                active_ve_bal += accounts[acct].vebalance
            i += 1
        pct = active_ve_bal / tot_ve_bal
    return pct


def behavior_vote_strategy_1(run, active_pct, assets: dict) -> Dict[uuid.UUID, float]:
    '''
    logic: "uniform random"
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
    logic: "perfect allocation"
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
    logic: "perfect distribution"
    - DCV is allocated to the ranked assets according to the same logrithmic distribution that is used in the rewards function.
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


def behavior_consume_stoch(timestep, assets, consume_probability, consume_multiple, min_dcv_amt, max_dcv_amt):
    '''
    logic: "stochastic"
    - weekly probability that a ranked asset is consumed = X% (so each asset has a chance to be consumed each week)
    - amount consumed = uniform random between 100 to 1000
    '''
    time_multiple = timestep
    signal = np.random.uniform(size=(len(assets)))
    assets_consumed = {}
    i=0
    for asset in assets.keys():
        if signal[i] < consume_probability:
            dcv = np.random.uniform(min_dcv_amt * time_multiple * consume_multiple
                                    , max_dcv_amt * time_multiple * consume_multiple)
            assets_consumed[asset] = dcv
            i += 1
    return assets_consumed