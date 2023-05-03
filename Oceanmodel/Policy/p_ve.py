import sys
sys.path.append("C:/Users/Surface/Documents/repos/playground")

# policies put inputs to the mechanisms and output changes to state/stateful metric 
import Oceanmodel.Mechanism.m_ve as m
import Oceanmodel.behavior.b_ve as b

def p_lock_ocean(params, substep, state_history, previous_state):
    amt, t = b.behavior_lockocean(previous_state['timestep'] + 1)
    ocean, _ = m.lockocean(amt, t)
    return {'new_locked_ocean': ocean}

def p_set_veaccount_params_duration(params, substep, state_history, previous_state):
    amt, t = b.behavior_lockocean(previous_state['timestep'] + 1)
    _, duration = m.lockocean(amt, t)
    return {'new_account_duration': duration}

def p_set_veaccount_params_timestamp(params, substep, state_history, previous_state):
    starting_timestep = previous_state['timestep'] + 1
    return {'new_starting_timestep': starting_timestep}

# update withdrawn amount according to 'behavior_withdraw'
def p_withdraw_ocean(params, substep, state_history, previous_state):
    ocean = m.withdrawocean(b.behavior_withdraw(previous_state['timestep']))
    return {'new_withdrawn_ocean': ocean}

# update unlocked amt (amt will be recalculated and previous state overwritten) needs to run after 'withdrawn',
def p_rebalance_unlocked_ocean(params, substep, state_history, previous_state):
    unlockedocean = previous_state['veaccount_1_initialocean'] * (previous_state['timestep'] - previous_state['veaccount_1_lockperiodstart'])/previous_state['veaccount_1_lockduration'] - previous_state['veaccount_1_withdrawn']
    return {'total_unlocked': unlockedocean}
# update locked amt. needs to run after 'rebalance unlocked' and 'withdraw'
def p_rebalance_locked_ocean(params, substep, state_history, previous_state):
    lockedocean = previous_state['veaccount_1_initialocean'] - previous_state['veaccount_1_unlocked'] - previous_state['veaccount_1_withdrawn']
    return {'rebalancedocean_locked': lockedocean}
# update veOcean balance according to ve votes decrease mechanism
def p_rebalance_veocean(params, substep, state_history, previous_state):
    balance = previous_state['veaccount_1_initialocean'] * (previous_state['veaccount_1_lockduration'] - (previous_state['timestep'] - previous_state['veaccount_1_lockperiodstart'])) / params['vecontract_maxlock']
    return {'total_veocean_balance': balance}

# update data asset for veallocation according to 'behavior vote' needs to run at the beginning of step!
def p_set_vote_data_asset(params, substep, state_history, previous_state):
    a, p = b.behavior_vote(previous_state['timestep'] + 1)
    data_asset, _ = m.vote(a, p)
    return {'vote_data_asset': data_asset}

# update percent for veallocation according to 'behavior vote' needs to run at the beginning of step!
def p_set_vote_percent(params, substep, state_history, previous_state):
    a, p = b.behavior_vote(previous_state['timestep'] + 1)
    _, percent = m.vote(a, p)
    return {'vote_percent': percent}

def p_aggregate_votes(params, substep, state_history, previous_state):
    veocean = previous_state['veaccount_1_vebalance'] * previous_state['veaccount_1_asset_1_votepercent']
            #+ previous_state['veaccount_2_vebalance'] * previous_state['veaccount_2_asset_1_votepercent']
    return {'data_asset_1_votes': veocean}