# at a given timestep, initialize a veOcean account by locking ocean
from typing import *
import random
import uuid
        
## According to logic (at timestep X) set the ve allocation percent for a data asset
#def behavior_vote(timestep) -> Tuple[int, float]:
#    if timestep == 20:
#        asset = 1
#        vote = 0.25
#    elif timestep == 60:
#        asset = 1
#        vote = 0.4
#    elif timestep == 100:
#        asset = 1
#        vote = 0.0
#    else:
#        asset = 0
#        vote = 0.0
#    return asset, vote


def behavior_move_ocean(timestep: int, oceanholders: dict, veaccounts: dict, minlock: int, maxlock: int) -> Dict[str, list]:
    '''
    # logic to determine which ocean holder agents lock ocean
    # current logic: every X timesteps, an ocean holder with positive ocean balance locks X ocean for Y days.
    #                From all ocean holders with positive balance, lock a random amt (or all if balance < random amt) for Y days
    '''
    if timestep % 20 == 0:
        action_lock = 'lock'
        valid_locking_agents = [key for key in oceanholders.keys() if oceanholders[key].oceanbalance > 0]

        selected_locking_agent = random.choice(valid_locking_agents)
        ocean_balance = oceanholders[selected_locking_agent].oceanbalance
        lock_amount = min(random.uniform(0.0,2*ocean_balance), ocean_balance) #max=2*balance so that we empty balance 50% of the time and don't lock tiny amounts
        lock_duration = random.uniform(minlock, maxlock)
        new_veaccount = 'dummy'
    else:
        action_lock = 'none'
        selected_locking_agent = '0'
        lock_amount = 0
        lock_duration = 0
        new_veaccount = 'dummy'

    # Logic determines which agents withdraw their unlocked ocean. EXCLUDING any agent who is locking ocean.
    if timestep % 25 == 0:
        # iterate through all ocean holders with positive balance of unlocked tokens in a ve account
        action_withdraw = 'withdraw'
        #valid_withdrawing_agents = [key for key in oceanholders.keys() if [acct for acct in oceanholders[key].veaccounts if veaccounts[acct].unlocked > 0] in oceanholders[key].veaccounts and key not in selected_locking_agents]
        #valid_withdrawing_agents = [key for key in oceanholders.keys() if any(veaccounts[acct].unlocked > 0 for acct in oceanholders[key].veaccounts) and key not in selected_locking_agents]
        valid_withdrawing_agents = [key for key in oceanholders.keys() if key not in selected_locking_agent]
        selected_withdrawing_agent = random.choice(valid_withdrawing_agents)
        valid_veaccount = [acct for acct in oceanholders[selected_withdrawing_agent].veaccounts if veaccounts[acct].unlocked > 0]
        selected_veaccount = random.choice(valid_veaccount)

        unlocked_balance = veaccounts[selected_veaccount].unlocked
        withdraw_amount = min(random.uniform(0.0, 2*unlocked_balance), unlocked_balance) #max=2*balance so that we empty balance 50% of the time and don't leave tiny amounts
        withdraw_duration = 0 #n/a
    else:
        action_withdraw = 'none'
        selected_withdrawing_agent = '0'
        withdraw_amount = 0
        withdraw_duration = 0
        existing_veaccount = '0'

    # combine locking + withdrawing actions to output Dict. will make this a for loop to allow multiple locking & withdrawing agents
    acting_agents = {}
    acting_agents[selected_locking_agent] = (action_lock, lock_amount, lock_duration, new_veaccount)
    acting_agents[selected_withdrawing_agent] = (action_withdraw, withdraw_amount, withdraw_duration, existing_veaccount)

    return acting_agents