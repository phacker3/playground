import sys
#sys.path.append("C:/Users/Surface/Documents/repos/playground")
sys.path.append("/home/peterhacker/Documents/phRepo/playground")


# policies put inputs to the mechanisms and output changes to state/stateful metric 
import Oceanmodel.mechanism_ve as m
import Oceanmodel.behavior_ve as b
import Oceanmodel.agents_ve as a

## policies related to an ocean holder locking ocean and creating a new ve account

def p_lock_withdraw_ocean(params, substep, state_history, previous_state):
    behavior_data = b.behavior_move_ocean(previous_state['timestep']+1,
                                          previous_state['agents_oceanholder'],
                                          previous_state['agents_veaccount'],
                                          params['vecontract_minlock'],
                                          params['vecontract_maxlock'])
    
    sent_ocean = {}
    initialized_veaccount = {}
    received_ocean = {}
    withdrawn_ocean = {}

    for agent in behavior_data.keys():
        if behavior_data[agent][0] == 'lock':
            '''
            pair agent id with delta for the following state changes:
              > subtract ocean_amounts from agents_oceanholder[].oceanbalance
              > initialize new_account = a.create_new_agent_veaccount(ocean_amounts, durations, previous_state['timestep']+1)
              > append agents_oceanholder.veaccounts with id from new_account
            '''

            # add key-value pair to dict: pair agent id with sent ocean amount
            sent_ocean[agent] = [behavior_data[agent][1]]
            # add key-value pair to dict: pair agent id with newly initialized veaccount
            initialized_veaccount[agent] = a.create_new_agent_veaccount(behavior_data[agent][1], behavior_data[agent][2], previous_state['timestep']+1)
        if behavior_data[agent][0] == 'withdraw':
            '''
            pair agent id with delta for the following state changes:
                > add ocean_amounts to agents_oceanholder.oceanbalance
                > subtract ocean_amounts from veaccount.unlocked
                > add ocean_amounts to veaccount.withdrawn
            '''

            # add key-value pair to dict: pair agent id with ocean amount being received
            received_ocean[agent] = [behavior_data[agent][1]]
            # add key-value pair to dict: pair agent id with ocean amount being withdrawn
            withdrawn_ocean[behavior_data[agent][3]] = [behavior_data[agent][1]]
    return {'sent_ocean': sent_ocean, 'initialized_veaccount': initialized_veaccount, 'received_ocean': received_ocean, 'withdrawn_ocean': withdrawn_ocean}


## update unlocked amt (amt will be recalculated and previous state overwritten) needs to run after 'withdrawn',
#def p_rebalance_unlocked_ocean(params, substep, state_history, previous_state):
#    if previous_state['veaccount_1_initialocean'] == 0:
#        unlockedocean = 0
#    else:
#        unlockedocean = previous_state['veaccount_1_initialocean'] * (previous_state['timestep'] - previous_state['veaccount_1_lockperiodstart'])/previous_state['veaccount_1_lockduration'] - previous_state['veaccount_1_withdrawn']
#    return {'total_unlocked': min(unlockedocean, previous_state['veaccount_1_initialocean'] - previous_state['veaccount_1_withdrawn'])}
## update locked amt. needs to run after 'rebalance unlocked' and 'withdraw'
#def p_rebalance_locked_ocean(params, substep, state_history, previous_state):
#    lockedocean = previous_state['veaccount_1_initialocean'] - previous_state['veaccount_1_unlocked'] - previous_state['veaccount_1_withdrawn']
#    return {'rebalancedocean_locked': lockedocean}
## update veOcean balance according to ve votes decrease mechanism
#def p_rebalance_veocean(params, substep, state_history, previous_state):
#    balance = previous_state['veaccount_1_initialocean'] * (previous_state['veaccount_1_lockduration'] - (previous_state['timestep'] - previous_state['veaccount_1_lockperiodstart'])) / params['vecontract_maxlock']
#    return {'total_veocean_balance': max(balance, 0)}
#
## update data asset for veallocation according to 'behavior vote' needs to run at the beginning of step!
#def p_set_vote_data_asset(params, substep, state_history, previous_state):
#    a, p = b.behavior_vote(previous_state['timestep'] + 1)
#    data_asset, _ = m.vote(a, p)
#    return {'vote_data_asset': data_asset}
#
## update percent for veallocation according to 'behavior vote' needs to run at the beginning of step!
#def p_set_vote_percent(params, substep, state_history, previous_state):
#    a, p = b.behavior_vote(previous_state['timestep'] + 1)
#    #p = b.behavior_vote(previous_state['timestep'] + 1)
#    _, percent = m.vote(a, p)
#    #percent = m.vote(p)
#    return {'vote_percent': percent}
#
#def p_aggregate_votes(params, substep, state_history, previous_state):
#    veocean = previous_state['veaccount_1_vebalance'] * previous_state['veaccount_1_asset_1_votepercent']
#            #+ previous_state['veaccount_2_vebalance'] * previous_state['veaccount_2_asset_1_votepercent']
#    return {'data_asset_1_votes': veocean}