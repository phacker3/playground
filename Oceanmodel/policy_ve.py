import sys
#sys.path.append("C:/Users/Surface/Documents/repos/playground")
sys.path.append("/home/peterhacker/Documents/phRepo/playground")


# policies put inputs to the mechanisms and output changes to state/stateful metric 
import Oceanmodel.mechanism_ve as m
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