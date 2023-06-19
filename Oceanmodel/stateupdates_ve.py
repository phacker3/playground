def s_agents_oceanholder_lock_withdraw(params, substep, state_history, previous_state, policy_input):
    # iterate through the agents in each policy signal and update their corresponding dataclass object / state variable
    agents_oceanholder = previous_state['agents_oceanholder']
    for agent in policy_input['sent_ocean'].keys():
        agents_oceanholder[agent].oceanbalance -= policy_input['sent_ocean'][agent][0] #subtract sent ocean from oceanholder balance
    for agent in policy_input['received_ocean'].keys():
        agents_oceanholder[agent].oceanbalance += policy_input['received_ocean'][agent][0] #add received ocean from oceanholder balance (after withdraw)
    for agent in policy_input['initialized_veaccount'].keys():
        agents_oceanholder[agent].veaccounts[policy_input['initialized_veaccount'][agent].id] = policy_input['initialized_veaccount'][agent] #add new veaccount to oceanholder veaccounts dict (after lock)
    for agent in policy_input['withdrawn_ocean'].keys():
        for acct in policy_input['withdrawn_ocean'][agent].keys():
            agents_oceanholder[agent].veaccounts[acct].unlocked -= policy_input['withdrawn_ocean'][agent][acct] #subtract withdrawn ocean from veaccount balance of unlocked ocean
            agents_oceanholder[agent].veaccounts[acct].withdrawn += policy_input['withdrawn_ocean'][agent][acct] #add withdrawn ocean to veaccount record of withdrawn ocean
    #print('state update1 complete')
    return 'agents_oceanholder', agents_oceanholder


def s_agents_oceanholder_rebalance(params, substep, state_history, previous_state, policy_input):
    # iterate through aagents AND their ve accounts in each policy signal and replace their balances of locked, unlocked, and veocean
    agents_oceanholder = previous_state['agents_oceanholder']
    for agent in policy_input['locked_balances'].keys():
        for acct in policy_input['locked_balances'][agent].keys():
            agents_oceanholder[agent].veaccounts[acct].locked = policy_input['locked_balances'][agent][acct]
            agents_oceanholder[agent].veaccounts[acct].unlocked = policy_input['unlocked_balances'][agent][acct]
            agents_oceanholder[agent].veaccounts[acct].vebalance = policy_input['veocean_balances'][agent][acct]
    return 'agents_oceanholder', agents_oceanholder


#def s_agents_veaccount(params, substep, state_history, previous_state, policy_input):
#    # iterate through agents_oceanholder and update the dataclass object with any delta policy signals
#    agents_veaccount = previous_state['agents_veaccount']
#    # match existing veaccounts with accounts that have a withdraw 
#    for account in agents_veaccount.keys():
#        for account in policy_input['withdrawn_ocean'].keys():
#            agents_veaccount[account].unlocked -= policy_input['withdrawn_ocean'][account][0] #subtract
#            agents_veaccount[account].withdrawn += policy_input['withdrawn_ocean'][account][0] #add
#    # add new key-value pair
#    for agent in policy_input['initialized_veaccount'].keys():
#        agents_veaccount[policy_input['initialized_veaccount'][agent].id] = policy_input['initialized_veaccount'][agent]
#
#    return 'agents_veaccount', agents_veaccount

#def s_oceanholderbalance(params, substep, state_history, previous_state, policy_input):
#    balance = previous_state['oceanholder_oceanbalance'] - policy_input['new_locked_ocean'] + policy_input['new_withdrawn_ocean']
#    return 'oceanholder_oceanbalance', balance
#
## takes policy inputs related to the balance of unlocked Ocean and returns a new state
#def s_unlockedocean(params, substep, state_history, previous_state, policy_input):
#    unlocked_amount = policy_input['total_unlocked']
#    return 'veaccount_1_unlocked', unlocked_amount
#
## takes policy inputs related to the balance of ve tokens and returns a new state
#def s_veocean_balance(params, substep, state_history, previous_state, policy_input):
#    balance = policy_input['total_veocean_balance']
#    return 'veaccount_1_vebalance', balance
#
## takes policy inputs related to setting data asset number and allocation precent and returning a new state
#def s_data_asset_pct(params, substep, state_history, previous_state, policy_input):
#    if policy_input['vote_data_asset'] == 1:
#    #if policy_input['vote_percent'] > 0:
#        pct = policy_input['vote_percent']
#    else:
#        pct = previous_state['veaccount_1_asset_1_votepercent']
#    return 'veaccount_1_asset_1_votepercent', pct
#
## takes policy inputs related to calculating the votes on data asset #1, and returns a new state
#def s_aggvotes(params, substep, state_history, previous_state, policy_input):
#    votes = policy_input['data_asset_1_votes']
#    return 'asset_1_veallocation', votes
#