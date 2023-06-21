def s_agents_oceanholder_behaviors(params, substep, state_history, previous_state, policy_input):
    # iterate through the agents in each policy signal and update their corresponding dataclass object / state variable
    agents_oceanholder = previous_state['agents_oceanholder']
    # locking
    for agent in policy_input['sent_ocean'].keys():
        agents_oceanholder[agent].oceanbalance -= policy_input['sent_ocean'][agent][0] #subtract sent ocean from oceanholder balance
    for agent in policy_input['initialized_veaccount'].keys():
        agents_oceanholder[agent].veaccounts[policy_input['initialized_veaccount'][agent].id] = policy_input['initialized_veaccount'][agent] #add new veaccount to oceanholder veaccounts dict (after lock)
    # withdrawing
    for agent in policy_input['received_ocean'].keys():
        agents_oceanholder[agent].oceanbalance += policy_input['received_ocean'][agent][0] #add received ocean from oceanholder balance (after withdraw)
    for agent in policy_input['withdrawn_ocean'].keys():
        for acct in policy_input['withdrawn_ocean'][agent].keys():
            agents_oceanholder[agent].veaccounts[acct].unlocked -= policy_input['withdrawn_ocean'][agent][acct] #subtract withdrawn ocean from veaccount balance of unlocked ocean
            agents_oceanholder[agent].veaccounts[acct].withdrawn += policy_input['withdrawn_ocean'][agent][acct] #add withdrawn ocean to veaccount record of withdrawn ocean
    # voting
    for agent in policy_input['set_votes'].keys():
            for asset in policy_input['set_votes'][agent].keys():
                agents_oceanholder[agent].votepercent[asset] = policy_input['set_votes'][agent][asset]
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

#def s_agents_oceanholder_vote(params, substep, state_history, previous_state, policy_input):
#    agents_oceanholder = previous_state['agents_oceanholder']
#    for agent in policy_input['set_votes'].keys():
#        for asset in policy_input['set_votes'][agent].keys():
#            agents_oceanholder[agent].votepercent[asset] = policy_input['set_votes'][agent][asset]
#    return 'agents_oceanholder', agents_oceanholder

def s_agents_data_asset_aggregate_votes(params, substep, state_history, previous_state, policy_input):
    agents_data_asset = previous_state['agents_data_asset']
    for asset in policy_input['data_asset_agg_votes'].keys():
        agents_data_asset[asset].veallocation = policy_input['data_asset_agg_votes'][asset]
    return 'agents_data_asset', agents_data_asset 