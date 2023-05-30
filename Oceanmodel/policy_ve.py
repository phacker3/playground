import sys
#sys.path.append("C:/Users/Surface/Documents/repos/playground")
sys.path.append("/home/peterhacker/Documents/phRepo/playground")


# policies put inputs to the mechanisms and output changes to state/stateful metric 
import Oceanmodel.mechanism_ve as m
import Oceanmodel.behavior_ve as b
import Oceanmodel.agents_ve as a

# policies related to an ocean holder locking ocean and creating a new ve account
def p_lock_ocean(params, substep, state_history, previous_state):
    values = b.behavior_lockocean(previous_state['timestep']+1,
                                previous_state['agents_oceanholder'],
                                params['vecontract_minlock'],
                                params['vecontract_maxlock'])
    oceanholder = values.keys()
    amt = values[oceanholder][0]
    acct = values[oceanholder][2]
    
    return {'delta_locked_ocean': (oceanholder, amt, acct)} #referenced to decrease oceanholder ocean balance, and increase veaccount locked balance

def p_new_ve_account(params, substep, state_history, previous_state):
    values = b.behavior_lockocean(previous_state['timestep']+1,
                                  previous_state['agents_oceanholder'],
                                  params['vecontract_minlock'],
                                  params['vecontract_maxlock'])
    oceanholder = values.keys()
    amt = values[oceanholder][0]
    dur = values[oceanholder][1]
    acct = values[oceanholder][2]

    init_timestamp = previous_state['timestep']+1

    return {'new_ve_account': {acct, (amt, dur, init_timestamp)}} #referenced to initialize veaccount params

# policies related to an ocean holder withdrawing ocean
def p_withdraw_ocean(params, substep, state_history, previous_state):
    values = b.behavior_withdraw(previous_state['timestep']+1,
                                 previous_state['agents_oceanholder'],
                                 previous_state['agents_veaccount'])
    oceanholder = values.keys()
    acct = values[oceanholder][0]
    amt = values[oceanholder][1]

    return {'delta_withdrawn_ocean': (oceanholder, amt, acct)} #referenced to increase oceanholders ocean balance, and increase veaccount withdrawn balance

def p_lock_withdraw_ocean(params, substep, state_history, previous_state):
    values = b.behavior_move_ocean(previous_state['timestep']+1,
                                   previous_state['agents_oceanholder'],
                                   previous_state['agents_veaccount'],
                                   params['vecontract_minlock'],
                                   params['vecontract_maxlock'])
    
    # if action is 'lock'
    #   > Oceanholder: subtract ocean_amounts and append veaccounts
    #   > veaccount: initialize veaccounts, add ocean_amounts, initialize parameters
    if values
    # if action is 'withdraw'
    #   > Oceanholder: add ocean_amounts
    #   > veaccount: subtract unlocked amount, increase withdrawn amount

    return {'delta_ocean': ()}



# update withdrawn amount according to 'behavior_withdraw'
def p_withdraw_ocean(params, substep, state_history, previous_state):
    ocean = m.withdrawocean(b.behavior_withdraw(previous_state['timestep']))
    return {'new_withdrawn_ocean': ocean}

# update unlocked amt (amt will be recalculated and previous state overwritten) needs to run after 'withdrawn',
def p_rebalance_unlocked_ocean(params, substep, state_history, previous_state):
    if previous_state['veaccount_1_initialocean'] == 0:
        unlockedocean = 0
    else:
        unlockedocean = previous_state['veaccount_1_initialocean'] * (previous_state['timestep'] - previous_state['veaccount_1_lockperiodstart'])/previous_state['veaccount_1_lockduration'] - previous_state['veaccount_1_withdrawn']
    return {'total_unlocked': min(unlockedocean, previous_state['veaccount_1_initialocean'] - previous_state['veaccount_1_withdrawn'])}
# update locked amt. needs to run after 'rebalance unlocked' and 'withdraw'
def p_rebalance_locked_ocean(params, substep, state_history, previous_state):
    lockedocean = previous_state['veaccount_1_initialocean'] - previous_state['veaccount_1_unlocked'] - previous_state['veaccount_1_withdrawn']
    return {'rebalancedocean_locked': lockedocean}
# update veOcean balance according to ve votes decrease mechanism
def p_rebalance_veocean(params, substep, state_history, previous_state):
    balance = previous_state['veaccount_1_initialocean'] * (previous_state['veaccount_1_lockduration'] - (previous_state['timestep'] - previous_state['veaccount_1_lockperiodstart'])) / params['vecontract_maxlock']
    return {'total_veocean_balance': max(balance, 0)}

# update data asset for veallocation according to 'behavior vote' needs to run at the beginning of step!
def p_set_vote_data_asset(params, substep, state_history, previous_state):
    a, p = b.behavior_vote(previous_state['timestep'] + 1)
    data_asset, _ = m.vote(a, p)
    return {'vote_data_asset': data_asset}

# update percent for veallocation according to 'behavior vote' needs to run at the beginning of step!
def p_set_vote_percent(params, substep, state_history, previous_state):
    a, p = b.behavior_vote(previous_state['timestep'] + 1)
    #p = b.behavior_vote(previous_state['timestep'] + 1)
    _, percent = m.vote(a, p)
    #percent = m.vote(p)
    return {'vote_percent': percent}

def p_aggregate_votes(params, substep, state_history, previous_state):
    veocean = previous_state['veaccount_1_vebalance'] * previous_state['veaccount_1_asset_1_votepercent']
            #+ previous_state['veaccount_2_vebalance'] * previous_state['veaccount_2_asset_1_votepercent']
    return {'data_asset_1_votes': veocean}