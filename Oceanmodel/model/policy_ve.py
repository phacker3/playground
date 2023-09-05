import sys
#sys.path.append("C:/Users/Surface/Documents/repos/playground")
sys.path.append("/home/peterhacker/Documents/phRepo/playground")

import scipy
import numpy as np

import Oceanmodel.model.behavior_ve as b
import Oceanmodel.model.agents_ve as a

def p_lock_1(params, substep, state_history, previous_state):
    locked_supply = 0
    for acct in previous_state['ve_accounts'].keys():
        locked_supply += previous_state['ve_accounts'][acct].locked

    ocean_locked, lock_duration = b.behavior_lock_1(previous_state['run'],
                                                  previous_state['timestep'],
                                                  previous_state['ocean_unlocked_supply'],
                                                  locked_supply,
                                                  params['minlock_dur'],
                                                  params['maxlock_dur'],
                                                  params['lock_supply_pct_cap'])
    
    new_ve_acct = a.create_new_agent_veaccount(ocean_locked, lock_duration, previous_state['timestep']+1, params['maxlock_dur'])
    return {'ocean_circ_delta': -ocean_locked, 'initialized_veaccount': np.array([new_ve_acct])}

def p_lock_2(params, substep, state_history, previous_state):
    locked_supply = 0
    for acct in previous_state['ve_accounts'].keys():
        locked_supply += previous_state['ve_accounts'][acct].locked

    ocean_locked, lock_duration = b.behavior_lock_2(previous_state['distribution_schedule'][previous_state['timestep']][0] * (1 - params['datafarming_active_share'])
                                                  , previous_state['rewards_pool_fees']
                                                  , params['min_accepted_yield']['weekly_yield']
                                                  , previous_state['ocean_unlocked_supply']
                                                  , locked_supply
                                                  , params['minlock_dur']
                                                  , params['maxlock_dur']
                                                  , params['lock_supply_pct_cap'])
    
    new_ve_acct = a.create_new_agent_veaccount(ocean_locked, lock_duration, previous_state['timestep']+1, params['maxlock_dur'])
    return {'ocean_circ_delta': -ocean_locked, 'initialized_veaccount': np.array([new_ve_acct])}

def p_lock_3(params, substep, state_history, previous_state):
    locked_supply = 0
    for acct in previous_state['ve_accounts'].keys():
        locked_supply += previous_state['ve_accounts'][acct].locked

    passive_rewards = previous_state['distribution_schedule'][previous_state['timestep']][0] * (1 - params['datafarming_active_share'])
    active_rewards = previous_state['distribution_schedule'][previous_state['timestep']][0] * params['datafarming_active_share']

    ocean_locked, lock_duration = b.behavior_lock_3(passive_rewards
                                                  , previous_state['rewards_pool_fees']
                                                  , active_rewards
                                                  , params['min_accepted_yield']['weekly_yield']
                                                  , previous_state['ocean_unlocked_supply']
                                                  , locked_supply
                                                  , params['minlock_dur']
                                                  , params['maxlock_dur']
                                                  , params['lock_supply_pct_cap'])
    
    new_ve_acct = a.create_new_agent_veaccount(ocean_locked, lock_duration, previous_state['timestep']+1, params['maxlock_dur'])
    return {'ocean_circ_delta': -ocean_locked, 'initialized_veaccount': np.array([new_ve_acct])}

def p_lock_stoch(params, substep, state_history, previous_state):
    ocean_locked, lock_duration = b.behavior_lock_stoch(previous_state['ocean_unlocked_supply']
                                                        , params['weekly_lock_prob']
                                                        , params['minlock_amt']
                                                        , params['maxlock_amt']
                                                        , params['lock_dur']['min_lock']
                                                        , params['lock_dur']['max_lock'])
                                                        #, params['minlock_dur']
                                                        #, params['maxlock_dur'])
    new_ve_acct = np.array([])
    for i in range(len(ocean_locked)):
        new_ve_acct = np.append(new_ve_acct, a.create_new_agent_veaccount(ocean_locked[i], lock_duration[i], previous_state['timestep']+1, params['maxlock_dur']))
    return {'ocean_circ_delta': -sum(ocean_locked), 'initialized_veaccount': new_ve_acct}

def p_rebalance(params, substep, state_history, previous_state):
    accts = previous_state['ve_accounts']
    t = previous_state['timestep']

    locked_balances = {}
    ve_balances = {}
    unlock_tot = 0
    for acct in accts.keys():
        acct_data = accts[acct]
        if t+1 > acct_data.lockperiodstart + acct_data.lockduration:
            locked_bal = 0
            ve_bal = 0
        else:
            locked_bal = acct_data.initialocean - (acct_data.initialocean * (t+1 - acct_data.lockperiodstart)/acct_data.lockduration)
            ve_bal = acct_data.initialocean * (acct_data.lockduration - (t+1 - acct_data.lockperiodstart)) / params['maxlock_dur']
        unlocked_amt = acct_data.locked - locked_bal
        locked_balances[acct] = locked_bal
        ve_balances[acct] = ve_bal
        unlock_tot += unlocked_amt
    return {'ocean_circ_delta': unlock_tot, 'locked_balances': locked_balances, 'veocean_balances': ve_balances}


def p_vote_1(params, substep, state_history, previous_state):
    active_pct = b.behavior_vote_active_1()
    behavior_data = b.behavior_vote_strategy_1(previous_state['run']
                                               , active_pct
                                               , previous_state['data_assets'])
    return {'set_votes': behavior_data}

def p_vote_2(params, substep, state_history, previous_state):
    active_pct = b.behavior_vote_active_1()
    behavior_data = b.behavior_vote_strategy_2(previous_state['run']
                                               , active_pct
                                               , previous_state['data_assets']
                                               , params['datafarming_max_assets_n'])
    return {'set_votes': behavior_data}

def p_vote_3(params, substep, state_history, previous_state):
    locked_supply = 0
    for acct in previous_state['ve_accounts'].keys():
        locked_supply += previous_state['ve_accounts'][acct].locked

    tot_dcv = 0
    for asset in previous_state['data_assets'].keys():
        tot_dcv += previous_state['data_assets'][asset].dataconsumevolume

    eligible_rewards_passive = previous_state['distribution_schedule'][previous_state['timestep']][0] * (1 - params['datafarming_active_share'])
    eligible_rewards_active = previous_state['distribution_schedule'][previous_state['timestep']][0] * params['datafarming_active_share']
    eligible_rewards_fees = previous_state['rewards_pool_fees']
    min_weekly_yield = params['min_accepted_yield']['weekly_yield']
    df_yield_cap = params['datafarming_weekly_yield_cap']
    active_pct = b.behavior_vote_active_2(previous_state['timestep']
                                           , locked_supply
                                           , eligible_rewards_passive
                                           , eligible_rewards_active
                                           , eligible_rewards_fees
                                           , min_weekly_yield
                                           , tot_dcv
                                           , df_yield_cap)
    
    behavior_data = b.behavior_vote_strategy_1(previous_state['run']
                                               , active_pct
                                               , previous_state['data_assets'])
    return {'set_votes': behavior_data}

def p_vote_4(params, substep, state_history, previous_state):
    locked_supply = 0
    for acct in previous_state['ve_accounts'].keys():
        locked_supply += previous_state['ve_accounts'][acct].locked

    tot_dcv = 0
    for asset in previous_state['data_assets'].keys():
        tot_dcv += previous_state['data_assets'][asset].dataconsumevolume

    eligible_rewards_passive = previous_state['distribution_schedule'][previous_state['timestep']][0] * (1 - params['datafarming_active_share'])
    eligible_rewards_active = previous_state['distribution_schedule'][previous_state['timestep']][0] * params['datafarming_active_share']
    eligible_rewards_fees = previous_state['rewards_pool_fees']
    min_weekly_yield = params['min_accepted_yield']['weekly_yield']
    df_yield_cap = params['datafarming_weekly_yield_cap']

    active_pct = b.behavior_vote_active_2(previous_state['timestep']
                                           , locked_supply
                                           , eligible_rewards_passive
                                           , eligible_rewards_active
                                           , eligible_rewards_fees
                                           , min_weekly_yield
                                           , tot_dcv
                                           , df_yield_cap)
    behavior_data = b.behavior_vote_strategy_2(previous_state['run']
                                               , active_pct
                                               , previous_state['data_assets']
                                               , params['datafarming_max_assets_n'])
    return {'set_votes': behavior_data}

def p_vote_5(params, substep, state_history, previous_state):
    locked_supply = 0
    ve_bal = 0
    for acct in previous_state['ve_accounts'].keys():
        locked_supply += previous_state['ve_accounts'][acct].locked
        ve_bal += previous_state['ve_accounts'][acct].vebalance

    tot_dcv = 0
    for asset in previous_state['data_assets'].keys():
        tot_dcv += previous_state['data_assets'][asset].dataconsumevolume

    eligible_rewards_active = previous_state['distribution_schedule'][previous_state['timestep']][0] * params['datafarming_active_share']
    df_yield_cap = params['datafarming_weekly_yield_cap']

    active_pct = b.behavior_vote_active_3(previous_state['timestep']
                                           , ve_bal
                                           , eligible_rewards_active
                                           , tot_dcv
                                           , df_yield_cap)
    behavior_data = b.behavior_vote_strategy_2(previous_state['run']
                                               , active_pct
                                               , previous_state['data_assets']
                                               , params['datafarming_max_assets_n'])
    return {'set_votes': behavior_data}

def p_vote_stoch(params, substep, state_history, previous_state):
    active_pct = b.behavior_vote_active_stoch(previous_state['ve_accounts']
                                              , params['weekly_vote_success_prob'])
    behavior_data = b.behavior_vote_strategy_1(previous_state['run']
                                               , active_pct
                                               , previous_state['data_assets'])
    return {'set_votes': behavior_data}

def p_vote_stoch_2(params, substep, state_history, previous_state):
    active_pct = b.behavior_vote_active_stoch(previous_state['ve_accounts']
                                              , params['weekly_vote_success_prob'])
    behavior_data = b.behavior_vote_strategy_2(previous_state['run']
                                               , active_pct
                                               , previous_state['data_assets']
                                               , params['datafarming_max_assets_n'])
    return {'set_votes': behavior_data}

def p_active_rewards(params, substep, state_history, previous_state):
    # this rewards function can run every step, but rewards distributions will only happen according to the DistributionSchedule (i.e. when tokens are released to the rewards pools)
    # rank data assets by dataconsumevolume and return a list of the top 100
    data_assets = np.array([])
    dcv_rewards_period = np.array([])
    for asset in previous_state['data_assets'].keys():
        # to make ranking process simple, we need two identical arrays: one with data_assets, one with the corresponding DCV
        data_assets = np.append(data_assets, asset)
        dcv_rewards_period = np.append(dcv_rewards_period, previous_state['data_assets'][asset].dataconsumevolume)
    ranks = scipy.stats.rankdata(-1 * dcv_rewards_period, method='min')
    
    # Rank j - pct_j
    allocations = np.zeros_like(ranks)
    allocations = allocations.astype(float)
    top_indicies = np.where(ranks <= params['datafarming_max_assets_n'])
    logranks = np.log10(ranks)
    allocations[top_indicies] = max(logranks[top_indicies]) - logranks[top_indicies] + np.log10(1.5)
    allocations_normalized = allocations / np.sum(allocations)
    

    ve_bal = 0
    locked_supply = 0
    for acct in previous_state['ve_accounts'].keys():
        ve_bal += previous_state['ve_accounts'][acct].vebalance
        locked_supply += previous_state['ve_accounts'][acct].locked

    rewards = 0
    eligible_rewards = previous_state['distribution_schedule'][previous_state['timestep']][0] * params['datafarming_active_share']
    for asset in previous_state['data_assets'].keys():
        rewards += min(
            float(allocations_normalized[data_assets == asset] * eligible_rewards),
            float(previous_state['votes'][asset] * ve_bal * params['datafarming_weekly_yield_cap']),
            #float(previous_state['votes'][asset] * locked_supply * params['datafarming_weekly_yield_cap']),
            float(previous_state['data_assets'][asset].dataconsumevolume * 0.01)
        )
    return {'active_rewards': rewards, 'treasury_delta_ocean': -rewards, 'ocean_circ_delta': rewards}

def p_passive_and_fee_rewards(params, substep, state_history, previous_state):
    eligible_rewards_passive = previous_state['distribution_schedule'][previous_state['timestep']][0] * (1 - params['datafarming_active_share'])
    eligible_rewards_fees = previous_state['rewards_pool_fees']

    ve_bal = 0
    for acct in previous_state['ve_accounts'].keys():
        ve_bal += previous_state['ve_accounts'][acct].vebalance

    if ve_bal == 0:
        rewards_passive = 0
        rewards_fees = 0
    else:
        rewards_passive = eligible_rewards_passive
        rewards_fees = eligible_rewards_fees
    return {'passive_rewards': rewards_passive, 'fee_rewards': rewards_fees, 'treasury_delta_ocean': -rewards_passive, 'rewards_pool_fees_delta': -rewards_fees, 'ocean_circ_delta': rewards_passive + rewards_fees}


def p_data_asset_consumed_1(params, substep, state_history, previous_state):
    run = previous_state['run']
    timestep = previous_state['timestep']
    assets = previous_state['data_assets']

    dcv_amt = b.behavior_consume_amt_1(previous_state['timestep'])
    behavior_data = b.behavior_consume_distr_2(assets, dcv_amt)

    fees_paid = params['protocol_transaction_fee'] * sum(behavior_data.values())
    protocol_rev = fees_paid * (1 - params['revenue_burn_pct'])
    burned = fees_paid * params['revenue_burn_pct']
    return {'data_asset_consumed': behavior_data, 'rewards_pool_fees_delta': protocol_rev, 'ocean_circ_delta': -burned}

def p_data_asset_consumed_2(params, substep, state_history, previous_state):
    run = previous_state['run']
    timestep = previous_state['timestep']
    assets = previous_state['data_assets']

    dcv_amt = b.behavior_consume_amt_2(previous_state['timestep'])
    behavior_data = b.behavior_consume_distr_2(assets, dcv_amt)

    fees_paid = params['protocol_transaction_fee'] * sum(behavior_data.values())
    protocol_rev = fees_paid * (1 - params['revenue_burn_pct'])
    burned = fees_paid * params['revenue_burn_pct']
    return {'data_asset_consumed': behavior_data, 'rewards_pool_fees_delta': protocol_rev, 'ocean_circ_delta': -burned}

def p_data_asset_consumed_3(params, substep, state_history, previous_state):
    run = previous_state['run']
    timestep = previous_state['timestep']
    assets = previous_state['data_assets']

    dcv_amt = b.behavior_consume_amt_3(previous_state['timestep'])
    behavior_data = b.behavior_consume_distr_2(assets, dcv_amt)

    fees_paid = params['protocol_transaction_fee'] * sum(behavior_data.values())
    protocol_rev = fees_paid * (1 - params['revenue_burn_pct'])
    burned = fees_paid * params['revenue_burn_pct']
    return {'data_asset_consumed': behavior_data, 'rewards_pool_fees_delta': protocol_rev, 'ocean_circ_delta': -burned}

def p_data_asset_consumed_stoch(params, substep, state_history, previous_state):
    assets = previous_state['data_assets']

    behavior_data = b.behavior_consume_stoch(previous_state['timestep']
                                             , assets
                                             , params['weekly_consume_prob']
                                             , params['weekly_consume_multiple']
                                             , params['min_weekly_dcv_amt']
                                             , params['max_weekly_dcv_amt'])

    fees_paid = params['protocol_transaction_fee'] * sum(behavior_data.values())
    protocol_rev = fees_paid * (1 - params['revenue_burn_pct'])
    burned = fees_paid * params['revenue_burn_pct']
    return {'data_asset_consumed': behavior_data, 'rewards_pool_fees_delta': protocol_rev, 'ocean_circ_delta': -burned}

def p_data_asset_consumed_stoch_2(params, substep, state_history, previous_state):
    assets = previous_state['data_assets']

    behavior_data = b.behavior_consume_stoch(previous_state['timestep']
                                             , assets
                                             , params['weekly_consume_prob']
                                             , params['weekly_consume_multiple']
                                             , params['min_weekly_dcv_amt']
                                             , params['max_weekly_dcv_amt'])
    behavior_data = b.behavior_consume_distr_2(assets, sum(behavior_data.values()))

    fees_paid = params['protocol_transaction_fee'] * sum(behavior_data.values())
    protocol_rev = fees_paid * (1 - params['revenue_burn_pct'])
    burned = fees_paid * params['revenue_burn_pct']
    return {'data_asset_consumed': behavior_data, 'rewards_pool_fees_delta': protocol_rev, 'ocean_circ_delta': -burned}
