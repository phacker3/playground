# takes policy inputs related to the balance of locked Ocean and returns new state
def s_lock_ocean(params, substep, state_history, previous_state, policy_input):
    locked_amount = previous_state['veaccount_1_locked'] + policy_input['new_locked_ocean']
    return 'veaccount_1_locked', locked_amount
def s_locked_ocean(params, substep, state_history, previous_state, policy_input):
    locked_amount = policy_input['rebalancedocean_locked']
    return 'veaccount_1_locked', locked_amount
def s_oceanholderbalance(params, substep, state_history, previous_state, policy_input):
    balance = previous_state['oceanholder_oceanbalance'] - policy_input['new_locked_ocean'] + policy_input['new_withdrawn_ocean']
    return 'oceanholder_oceanbalance', balance

# takes policy inputs related to withdraw behavior for unlocked Ocean and returns new state
def s_withdrawnocean(params, substep, state_history, previous_state, policy_input):
    withdrawn_amount = previous_state['veaccount_1_withdrawn'] + policy_input['new_withdrawn_ocean']
    return 'veaccount_1_withdrawn', withdrawn_amount

# takes policy inputs related to the balance of unlocked Ocean and returns a new state
def s_unlockedocean(params, substep, state_history, previous_state, policy_input):
    unlocked_amount = policy_input['total_unlocked']
    return 'veaccount_1_unlocked', unlocked_amount

# sets duration parameter (implemented as a state) when ve account is initialized
def s_lockedocean_duration(params, substep, state_history, previous_state, policy_input):
    duration = previous_state['veaccount_1_lockduration'] + policy_input['new_account_duration']
    return 'veaccount_1_lockduration', duration
# sets start timestamp parameter (implemented as a state) when ve account is initialized
def s_lockedocean_starttimestamp(params, substep, state_history, previous_state, policy_input):
    timestamp = previous_state['veaccount_1_lockperiodstart'] + policy_input['new_starting_timestep']
    return 'veaccount_1_lockperiodstart', timestamp
# sets initial amount parameter (implemented as a state) when ve account is initialized [Pseudo parameter]
def s_lockedocean_initialamount(params, substep, state_history, previous_state, policy_input):
    amount = previous_state['veaccount_1_initialocean'] + policy_input['new_locked_ocean']
    return 'veaccount_1_initialocean', amount

# takes policy inputs related to the balance of ve tokens and returns a new state
def s_veocean_balance(params, substep, state_history, previous_state, policy_input):
    balance = policy_input['total_veocean_balance']
    return 'veaccount_1_vebalance', balance

# takes policy inputs related to setting data asset number and allocation precent and returning a new state
def s_data_asset_pct(params, substep, state_history, previous_state, policy_input):
    if policy_input['vote_data_asset'] == 1:
    #if policy_input['vote_percent'] > 0:
        pct = policy_input['vote_percent']
    else:
        pct = previous_state['veaccount_1_asset_1_votepercent']
    return 'veaccount_1_asset_1_votepercent', pct

# takes policy inputs related to calculating the votes on data asset #1, and returns a new state
def s_aggvotes(params, substep, state_history, previous_state, policy_input):
    votes = policy_input['data_asset_1_votes']
    return 'asset_1_veallocation', votes

