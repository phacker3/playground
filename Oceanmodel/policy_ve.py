import sys
#sys.path.append("C:/Users/Surface/Documents/repos/playground")
sys.path.append("/home/peterhacker/Documents/phRepo/playground")

import scipy
import numpy as np

# policies put inputs to the mechanisms and output changes to state/stateful metric 
import Oceanmodel.behavior_ve as b
import Oceanmodel.agents_ve as a

## policies related to an ocean holder locking ocean and creating a new ve account

def p_lock_withdraw(params, substep, state_history, previous_state):
    behavior_data = b.behavior_move_ocean(previous_state['timestep']+1,
                                          previous_state['agents_oceanholder'],
                                          #previous_state['agents_veaccount'],
                                          params['vecontract_minlock'],
                                          params['vecontract_maxlock'])
    
    sent_ocean = {}
    initialized_veaccount = {}
    received_ocean = {}
    withdrawn_ocean = {}

    for agent in behavior_data.keys():
        if behavior_data[agent][0] == 'lock':
            '''
            pair oceanholder agent id with policy signal delta for the following state changes:
              > subtract ocean_amounts from agents_oceanholder[].oceanbalance
              > initialize new_account = a.create_new_agent_veaccount(ocean_amounts, durations, previous_state['timestep']+1) and add this acct. to oceanholder veaccounts Dict as {key=new_account.id, value=new_account to agents_oceanholder.veaccounts}
            '''
            # add key-value pair to dict: pair agent id with sent ocean amount
            sent_ocean[agent] = [behavior_data[agent][1]]
            # add key-value pair to dict: pair agent id with newly initialized veaccount
            initialized_veaccount[agent] = a.create_new_agent_veaccount(behavior_data[agent][1], behavior_data[agent][2], previous_state['timestep']+1)
        if behavior_data[agent][0] == 'withdraw':
            '''
            pair oceanholder agent id with policy signal delta for the following state changes:
                > add ocean_amounts to agents_oceanholder.oceanbalance
                > subtract ocean_amounts from agents_oceanholder[agent].veaccount[behavior_data[agent][3]].unlocked
                > add ocean_amounts to agents_oceanholder[agent].veaccount.withdrawn
            '''
            # add key-value pair to dict: pair agent id with ocean amount being received
            received_ocean[agent] = [behavior_data[agent][1]]
            # add key-value pair to dict: pair agent id with ocean amount being withdrawn
            withdrawn_acct_amt = {}
            withdrawn_acct_amt[behavior_data[agent][3]] = behavior_data[agent][1]
            withdrawn_ocean[agent] = withdrawn_acct_amt
    return {'sent_ocean': sent_ocean, 'initialized_veaccount': initialized_veaccount, 'received_ocean': received_ocean, 'withdrawn_ocean': withdrawn_ocean}

def p_rebalance(params, substep, state_history, previous_state):
    # calculate deltas for unlocked and veocean balances
    unlocked_balances_agents = {}
    veocean_balances_agents = {}
    locked_balances_agents = {}
    for agent in previous_state['agents_oceanholder'].keys():
        unlocked_balances_accts = {}
        ve_balances_accts = {}
        locked_balances_accts = {}
        # skip the agent if previous_state['agents_oceanholder'][agent].veaccounts.keys() is empty
        if len(previous_state['agents_oceanholder'][agent].veaccounts.keys()) == 0:
            continue
        else:
            for acct in previous_state['agents_oceanholder'][agent].veaccounts.keys():
                acct_data = previous_state['agents_oceanholder'][agent].veaccounts[acct]
                # "skip" the account if lock duration is exceeded (acct closed)
                if (previous_state['timestep'] - acct_data.lockperiodstart) / acct_data.lockduration >= 1:
                    unlocked_amt = acct_data.initialocean - acct_data.withdrawn
                    ve_amt = 0
                    locked_amt = 0

                    unlocked_balances_accts[acct] = unlocked_amt
                    ve_balances_accts[acct] = ve_amt
                    locked_balances_accts[acct] = locked_amt
    
                else:
                    unlocked_amt = acct_data.initialocean * (previous_state['timestep'] - acct_data.lockperiodstart)/acct_data.lockduration - acct_data.withdrawn
                    ve_amt = acct_data.initialocean * (acct_data.lockduration - (previous_state['timestep'] - acct_data.lockperiodstart)) / params['vecontract_maxlock']
                    locked_amt = acct_data.initialocean - unlocked_amt - acct_data.withdrawn

                    unlocked_balances_accts[acct] = unlocked_amt
                    ve_balances_accts[acct] = ve_amt
                    locked_balances_accts[acct] = locked_amt

            unlocked_balances_agents[agent] = unlocked_balances_accts
            veocean_balances_agents[agent] = ve_balances_accts
            locked_balances_agents[agent] = locked_balances_accts
    return {'unlocked_balances': unlocked_balances_agents, 'veocean_balances': veocean_balances_agents, 'locked_balances': locked_balances_agents}


def p_vote(params, substep, state_history, previous_state):
    behavior_data = b.behavior_vote(previous_state['timestep']+1,
                                    previous_state['agents_oceanholder'],
                                    previous_state['agents_data_asset'])
    agent_asset_pct = {key: value for key, value in behavior_data.items() if key != '0'}
    return {'set_votes': agent_asset_pct}


# update data asset for veallocation according to 'behavior vote' needs to run at the beginning of step!
def p_aggregate_votes(params, substep, state_history, previous_state):
    # multiply each agent's vote percent by their ve balance
    data_asset_agg_votes = {}
    for asset in previous_state['agents_data_asset'].keys():
        agg_votes = 0
        for agent in previous_state['agents_oceanholder'].keys():
            agent_total_ve_balance = 0
            if asset in previous_state['agents_oceanholder'][agent].votepercent.keys():
                for acct in previous_state['agents_oceanholder'][agent].veaccounts.keys():
                    agent_total_ve_balance += previous_state['agents_oceanholder'][agent].veaccounts[acct].vebalance
                agg_votes += agent_total_ve_balance * previous_state['agents_oceanholder'][agent].votepercent[asset]
        data_asset_agg_votes[asset] = agg_votes
    return {'data_asset_agg_votes': data_asset_agg_votes}

# policy to release Ocean from the treasury to the active and passive rewards systems pools
def p_release_ocean(params, substep, state_history, previous_state):
    if (previous_state['timestep']) % 7 == 0:
        week_num = int(previous_state['timestep'] / 7)
        release_amt = previous_state['distribution_schedule'][week_num][0]
        active_rewards_amt = release_amt * params['datafarming_active_share']
        passive_rewards_amt = release_amt * (1-params['datafarming_active_share'])
    else:
        release_amt = 0
        active_rewards_amt = 0
        passive_rewards_amt = 0
    return {'treasury_delta_ocean': (-1 * release_amt), 'active_rewards_delta_ocean': active_rewards_amt, 'rewards_pool_df_passive_delta_ocean': passive_rewards_amt}

def p_rewards_matrix_snapshot(params, substep, state_history, previous_state):
    assset_ve_bal = {}
    agent_asset_ve_bal = {}
    # build rewards matrix for this step, with default zero as veOcean amount
    for agent in previous_state['agents_oceanholder'].keys():
        for asset in previous_state['agents_data_asset'].keys():
            assset_ve_bal[asset] = 0
            agent_asset_ve_bal[agent] = assset_ve_bal
        ve_bal = 0
        for acct in previous_state['agents_oceanholder'][agent].veaccounts.keys():
            ve_bal += previous_state['agents_oceanholder'][agent].veaccounts[acct].vebalance
        for asset in previous_state['agents_oceanholder'][agent].votepercent.keys():
            agent_asset_ve_bal[agent][asset] = previous_state['agents_oceanholder'][agent].votepercent[asset] * ve_bal
    return {'rewards_matrix_snapshot': agent_asset_ve_bal}
    

def p_active_rewards(params, substep, state_history, previous_state):
    # this rewards function can run every step, but rewards distributions will only happen according to the DistributionSchedule (i.e. when tokens are released to the rewards pools)
    # rank data assets by dataconsumevolume and return a list of the top 100
    data_assets = np.array([])
    dcv_rewards_period = np.array([])
    for asset in previous_state['agents_data_asset'].keys():
        # to make ranking process simple, we need two identical arrays: one with data_assets, one with the corresponding DCV_rewards_period
        data_assets = np.append(data_assets, asset)
        dcv_rewards_period = np.append(dcv_rewards_period, previous_state['agents_data_asset'][asset].dataconsumevolume_rewardsperiod)
    ranks = scipy.stats.rankdata(-1 * dcv_rewards_period, method='min')

    # Rank j - pct_j
    allocations = np.zeros_like(ranks)
    top_indicies = np.where(ranks <= params['datafarming_max_assets_n'])
    logranks = np.log10(ranks)
    allocations[top_indicies] = max(logranks[top_indicies]) - logranks[top_indicies] + np.log10(1.5)
    allocations_normalized = allocations / np.sum(allocations)

    # latest rewards matrix
    ij = previous_state['rewards_matrix']

    # get sum from the reward period of veAllocation for each asset
    j_tot = {}
    for asset in data_assets:
        j_tot[asset] = 0.0
        for agent in ij.keys():
            j_tot[asset] += ij[agent][asset]

    # main rewards function (incl. dcv and yield cap)
    i_rewards = {}
    for agent in previous_state['agents_oceanholder'].keys():
        i_rewards_amt = 0
        for asset in data_assets:
            if j_tot[asset] == 0:
                continue
            else:
                ij_pct = ij[agent][asset] / j_tot[asset]
                i_rewards_amt += min(
                    allocations_normalized[data_assets == asset] * ij_pct * previous_state['rewards_pool_df_active'], #pct_j*pct_ij*pool
                    ij[agent][asset] * params['datafarming_yield_cap'], #yield cap
                    previous_state['agents_data_asset'][asset].dataconsumevolume_rewardsperiod #dcv cap
                )
        #something in the min() function is causing the error... just overwrite nan for now
        if np.isnan(i_rewards_amt):
            i_rewards[agent] = 0
        else:
            i_rewards[agent] = i_rewards_amt
    
    # calculate surplus returned to treasury
    surplus_amt = (previous_state['rewards_pool_df_active'] - sum(i_rewards.values()))
    return {'oceanholder_active_rewards': i_rewards, 'treasury_delta_ocean': surplus_amt, 'active_rewards_delta_ocean': -(surplus_amt + sum(i_rewards.values()))}

def p_passive_and_fee_rewards(params, substep, state_history, previous_state):
    # latest rewards matrix
    ij = previous_state['rewards_matrix']
    # passive & fee rewards are based on veOcean balance held by each agent as % of total from that period
    # get sum from the reward period of veAllocation for each agent
    i_tot_ve = {}
    for agent in ij.keys():
        i_tot_ve[agent] = 0
        for asset in ij[agent].keys():
            i_tot_ve[agent] += ij[agent][asset]
    tot_ve = 0
    for agent in ij.keys():
        for asset in ij[agent].keys():
            tot_ve += ij[agent][asset]
    oceanholder_passive_rewards = {}
    oceanholder_fee_rewards = {}
    for agent in previous_state['agents_oceanholder'].keys():
        if tot_ve == 0:
            oceanholder_passive_rewards[agent] = 0
            oceanholder_fee_rewards[agent] = 0
        else:    
            i_pct = i_tot_ve[agent] / tot_ve
            oceanholder_passive_rewards[agent] = i_pct * previous_state['rewards_pool_df_passive'] # amt for passive rewards
            oceanholder_fee_rewards[agent] = i_pct * previous_state['rewards_pool_fees'] # amt for fees
    # If no ve tokens are staked, rewards will be 0 and surplus is sent back to treasury
    if sum(oceanholder_passive_rewards.values()) == 0:
        surplus_amt_passive = previous_state['rewards_pool_df_passive']
    else:
        surplus_amt_passive = 0
    
    if sum(oceanholder_fee_rewards.values()) == 0:
        surplus_amt_fees = previous_state['rewards_pool_fees']
    else:
        surplus_amt_fees = 0
    return {'oceanholder_passive_rewards': oceanholder_passive_rewards, 'oceanholder_fee_rewards': oceanholder_fee_rewards, 'rewards_pool_df_passive_delta_ocean': -(surplus_amt_passive + sum(oceanholder_passive_rewards.values())), 'rewards_pool_fees_delta_ocean': -(surplus_amt_fees + sum(oceanholder_fee_rewards.values())), 'treasury_delta_ocean': (surplus_amt_passive + surplus_amt_fees)}


def p_data_asset_consumed(params, substep, state_history, previous_state):
    # calculate the dataconsumed for each data asset
    behavior_data = b.behavior_consume_data(previous_state['timestep'], previous_state['agents_data_asset'])
    return {'data_asset_consumed': behavior_data}
