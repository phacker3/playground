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


def s_agents_data_asset_aggregate_votes(params, substep, state_history, previous_state, policy_input):
    agents_data_asset = previous_state['agents_data_asset']
    for asset in policy_input['data_asset_agg_votes'].keys():
        agents_data_asset[asset].veallocation = policy_input['data_asset_agg_votes'][asset]
    return 'agents_data_asset', agents_data_asset

# updates for main ocean pools
def s_treasury_ocean(params, substep, state_history, previous_state, policy_input):
    ocean_balance = previous_state['ocean_treasury'] + policy_input['treasury_delta_ocean']
    return 'ocean_treasury', ocean_balance
def s_data_farming_active_pool(params, substep, state_history, previous_state, policy_input):
    ocean_balance = previous_state['rewards_pool_df_active'] + policy_input['active_rewards_delta_ocean']
    return 'rewards_pool_df_active', ocean_balance
def s_data_farming_passive_pool(params, substep, state_history, previous_state, policy_input):
    ocean_balance = previous_state['rewards_pool_df_passive'] + policy_input['rewards_pool_df_passive_delta_ocean']
    return 'rewards_pool_df_passive', ocean_balance
def s_protocol_fees_pool(params, substep, state_history, previous_state, policy_input):
    ocean_balance = previous_state['rewards_pool_fees'] + policy_input['rewards_pool_fees_delta_ocean']
    return 'rewards_pool_fees', ocean_balance

# distribute rewards to ocean holders
def s_oceanholder_rewards_function(params, substep, state_history, previous_state, policy_input):
    agents_oceanholder = previous_state['agents_oceanholder']
    for agent in previous_state['agents_oceanholder'].keys():
        agents_oceanholder[agent].oceanbalance += (policy_input['oceanholder_passive_rewards'][agent]
                                                   + policy_input['oceanholder_fee_rewards'][agent]
                                                   + policy_input['oceanholder_active_rewards'][agent])
    return 'agents_oceanholder', agents_oceanholder

def s_data_asset_consumed(params, substep, state_history, previous_state, policy_input):
    agents_data_asset = previous_state['agents_data_asset']
    # update total DCV
    for asset in policy_input['data_asset_consumed'].keys():
        agents_data_asset[asset].dataconsumevolume = policy_input['data_asset_consumed'][asset]
    # update rewards period DCV
    for asset in policy_input['data_asset_consumed'].keys():
        if previous_state['timestep'] % 7 == 0:
            agents_data_asset[asset].dataconsumevolume_rewardsperiod = policy_input['data_asset_consumed'][asset]
        else:
            agents_data_asset[asset].dataconsumevolume_rewardsperiod += policy_input['data_asset_consumed'][asset]

    return 'agents_data_asset', agents_data_asset


def s_rewards_matrix(params, substep, state_history, previous_state, policy_input):
    # check whether to reset the rewards matrix (weekly)
    if previous_state['timestep'] % 7 == 0:
        rewards_matrix = previous_state['rewards_matrix']
        for agent in rewards_matrix.keys():
            for asset in rewards_matrix[agent].keys():
                rewards_matrix[agent][asset] = 0.0
    else:
        rewards_matrix = previous_state['rewards_matrix']

    # update the rewards matrix with the veOcean amounts for this step (try/except incase a new agent or asset... although, currently those agents are static after initialization, but this functionality will come later)
    for agent in policy_input['rewards_matrix_snapshot'].keys():
        for asset in policy_input['rewards_matrix_snapshot'][agent].keys():
            try:
                rewards_matrix[agent][asset] += policy_input['rewards_matrix_snapshot'][agent][asset]
            except:
                asset_amt = {asset: policy_input['rewards_matrix_snapshot'][agent][asset]}
                rewards_matrix[agent] = asset_amt
    return 'rewards_matrix', rewards_matrix