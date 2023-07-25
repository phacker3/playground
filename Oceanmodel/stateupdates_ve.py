def s_ocean_circ(params, substep, state_history, previous_state, policy_input):
    ocean_circ = previous_state['ocean_unlocked_supply']
    ocean_circ += policy_input['ocean_circ_delta']
    return 'ocean_unlocked_supply', ocean_circ

def s_new_ve_accounts(params, substep, state_history, previous_state, policy_input):
    ve_accounts = previous_state['ve_accounts']
    ve_accounts[policy_input['initialized_veaccount'].id] = policy_input['initialized_veaccount']
    return 've_accounts', ve_accounts
    
def s_votes(params, substep, state_history, previous_state, policy_input):
    votes = previous_state['votes']
    for asset in votes.keys():
        votes[asset] = policy_input['set_votes'][asset]
    return 'votes', votes


def s_rebalance_ve_accounts(params, substep, state_history, previous_state, policy_input):
    accts = previous_state['ve_accounts']
    for acct in accts.keys():
        accts[acct].locked = policy_input['locked_balances'][acct]
        accts[acct].vebalance = policy_input['veocean_balances'][acct]
    return 've_accounts', accts

def s_treasury_ocean(params, substep, state_history, previous_state, policy_input):
    ocean_balance = previous_state['ocean_treasury'] + policy_input['treasury_delta_ocean']
    return 'ocean_treasury', ocean_balance
def s_protocol_fees_pool(params, substep, state_history, previous_state, policy_input):
    ocean_balance = previous_state['rewards_pool_fees'] + policy_input['rewards_pool_fees_delta']
    return 'rewards_pool_fees', ocean_balance

def s_rewards_active(params, substep, state_history, previous_state, policy_input):
    reward = policy_input['active_rewards']
    return 'rewards_distributed_df_active', reward
def s_rewards_passive(params, substep, state_history, previous_state, policy_input):
    reward = policy_input['passive_rewards']
    return 'rewards_distributed_df_passive', reward
def s_rewards_fees(params, substep, state_history, previous_state, policy_input):
    reward = policy_input['fee_rewards']
    return 'rewards_distributed_fees', reward

def s_data_asset_consumed(params, substep, state_history, previous_state, policy_input):
    data_assets = previous_state['data_assets']
    # update total DCV
    for asset in data_assets.keys():
        data_assets[asset].dataconsumevolume = policy_input['data_asset_consumed'][asset]
    return 'data_assets', data_assets