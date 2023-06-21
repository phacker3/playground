# at a given timestep, initialize a veOcean account by locking ocean
from typing import *
import random
import uuid
        
# According to logic (at timestep X) set the ve allocation percent for a data asset
def behavior_vote(timestep, agents: dict, assets: dict) -> Dict[uuid.UUID, Dict[uuid.UUID, float]]:
    '''
    logic to determine which data asset an ocean holder allocates their VE ocean and how much (%)
    current logic: on timestep X, any ocean holder agent can set a % allocation for any number of data assets
    - can an agent set their votes and lock/withdraw in the same timestep? yes, so every agent is eligible
    - does an agent need a positive vebalance to set their vote? no, otherwise would need to automatically zero-out when ve balance decays to zero, and can't think of an issue with leaving it...
    - Note: need to restrict total percent allocated per agent <= 100%
    '''
    selected_data_assets_votes = {}
    if timestep % 200 == 0:
        valid_voting_agents = [key for key in agents.keys()]
        selected_voting_agents = random.choice(valid_voting_agents)
        valid_data_assets = [key for key in assets.keys()]
        if valid_data_assets:
            selected_data_assets = random.choice(valid_data_assets)
            if selected_data_assets in agents[selected_voting_agents].votepercent.keys():
                vote_pct = min(random.uniform(0.0,1.0), 1 - sum(agents[selected_voting_agents].votepercent.values()) + agents[selected_voting_agents].votepercent[selected_data_assets])
            else:
                vote_pct = min(random.uniform(0.0,1.0), 1 - sum(agents[selected_voting_agents].votepercent.values()))
            selected_data_assets_votes[selected_data_assets] = vote_pct
        else:
            selected_voting_agents = '0'
            selected_data_assets_votes['0'] = ['0.0']
    else:
        selected_voting_agents = '0'
        selected_data_assets_votes['0'] = ['0.0']

    acting_agents = {}
    acting_agents[selected_voting_agents] = selected_data_assets_votes
    return acting_agents

def behavior_move_ocean(timestep: int, oceanholders: dict, minlock: int, maxlock: int) -> Dict[uuid.UUID, list]:
    '''
    # logic to determine which ocean holder agents lock ocean
    # current logic: every X timesteps, an ocean holder with positive ocean balance locks X ocean for Y days.
    #                From all ocean holders with positive balance, lock a random amt (or all if balance < random amt) for Y days
    '''
    valid_locking_agents = [key for key in oceanholders.keys() if oceanholders[key].oceanbalance > 0]
    if timestep % 150 == 0 and valid_locking_agents:
        action_lock = 'lock'
        selected_locking_agents = random.choice(valid_locking_agents)
        ocean_balance = oceanholders[selected_locking_agents].oceanbalance
        lock_amount = min(random.uniform(0.0,2*ocean_balance), ocean_balance) #max=2*balance so that we empty balance 50% of the time and don't lock tiny amounts
        lock_duration = random.uniform(minlock, maxlock)
        new_veaccount = 'n/a'
    else:
        action_lock = 'none'
        selected_locking_agents = '0'
        lock_amount = 0
        lock_duration = 0
        new_veaccount = '0'

    valid_withdrawing_agents = [key for key in oceanholders.keys() if [acct for acct in oceanholders[key].veaccounts.keys() if oceanholders[key].veaccounts[acct].unlocked > 0] and key not in selected_locking_agents]
    # Logic determines which agents withdraw their unlocked ocean. EXCLUDING any agent who is locking ocean.
    if timestep % 250 == 0 and valid_withdrawing_agents:
        # iterate through all ocean holders with positive balance of unlocked tokens in a ve account
        action_withdraw = 'withdraw'
        selected_withdrawing_agents = random.choice(valid_withdrawing_agents)
        valid_veaccount = [acct for acct in oceanholders[selected_withdrawing_agents].veaccounts.keys() if oceanholders[selected_withdrawing_agents].veaccounts[acct].unlocked > 0]
        selected_veaccount = random.choice(valid_veaccount)
        unlocked_balance = oceanholders[selected_withdrawing_agents].veaccounts[selected_veaccount].unlocked
        withdraw_amount = min(random.uniform(0.0, 2*unlocked_balance), unlocked_balance) #max=2*balance so that we empty balance 50% of the time and don't leave tiny amounts
        withdraw_duration = 0 #n/a
    else:
        action_withdraw = 'none'
        selected_withdrawing_agents = '0'
        withdraw_amount = 0
        withdraw_duration = 0
        selected_veaccount = '0'

    # combine locking + withdrawing actions to output Dict. will make this a for loop to allow multiple locking & withdrawing agents
    acting_agents = {}
    acting_agents[selected_locking_agents] = (action_lock, lock_amount, lock_duration, new_veaccount)
    acting_agents[selected_withdrawing_agents] = (action_withdraw, withdraw_amount, withdraw_duration, selected_veaccount)

    return acting_agents