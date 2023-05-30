# at a given timestep, initialize a veOcean account by locking ocean
from typing import *
import random
import uuid

## according to logic (at timestep X), create a ve account for an ocean holder with non-zero balance
#def behavior_lockocean(timestep: int, oceanholders: dict, minlock: int, maxlock: int) -> Dict[int, list(float, int, str)]:
#    #logic: every X timesteps, an ocean holder with positive ocean balance locks X ocean for Y days
#    if timestep % 20 == 0:
#        #logic: from all ocean holders with positive balance, lock a random amt (or all if balance < random amt) for Y days
#        valid_oceanholder = [key for key in oceanholders.keys() if oceanholders[key]['oceanbalance'] > 0]
#        random_oceanholder = random.choice(valid_oceanholder)
#        ocean_balance = oceanholders[random_oceanholder]['oceanbalance']
#        lock_amount = random.random(0.0,2*ocean_balance) #max=2*balance so that we empty balance 50% of the time and don't lock tiny amounts
#        duration = random.random(minlock, maxlock)
#        account = uuid.uuid4()
#    else:
#        account = 0
#        random_oceanholder = 0
#        ocean_balance = 0
#        lock_amount = 0
#        duration = 0
#    return {random_oceanholder, (min(lock_amount, ocean_balance), duration, account)}
        
# According to logic (at timestep X) set the ve allocation percent for a data asset
def behavior_vote(timestep) -> Tuple[int, float]:
    if timestep == 20:
        asset = 1
        vote = 0.25
    elif timestep == 60:
        asset = 1
        vote = 0.4
    elif timestep == 100:
        asset = 1
        vote = 0.0
    else:
        asset = 0
        vote = 0.0
    return asset, vote

## according to logic (at timestep X), initiate a withdraw of unlocked ocean from an eligible ve account
#def behavior_withdraw(timestep: int, oceanholders: dict, veaccounts: dict) -> Dict[str, list(str, float)]:
#    #logic: every 100 timesteps, an ocean holder with eligble unlocked ocean balance in one of their ve accounts will withdraw that amount
#    if timestep % 100 == 0:
#        # iterate through all ocean holders with positive balance of unlocked tokens in a ve account
#        valid_oceanholder = [key for key in oceanholders.keys() if [acct for acct in oceanholders[key]['veaccounts'] if veaccounts[acct]['unlocked'] > 0] in oceanholders[key]['veaccounts']]
#        random_oceanholder = random.choice(valid_oceanholder)
#
#        valid_veaccount = [acct for acct in oceanholders[random_oceanholder]['veaccounts'] if veaccounts[acct]['unlocked'] > 0]
#        random_veaccount = random.choice(valid_veaccount)
#
#        unlocked_balance = veaccounts[random_veaccount]['unlocked']
#        withdraw_amount = random.random(0.0, 2*unlocked_balance) #max=2*balance so that we empty balance 50% of the time and don't leave tiny amounts
#    else:
#        random_oceanholder = 0
#        random_veaccount = 0
#        unlocked_balance = 0
#        withdraw_amount = 0
#    return {random_oceanholder, (random_veaccount, min(withdraw_amount, unlocked_balance))}
'''
!!!!!!!!!!!!!!!!!!!
- see miro for more ideas too

Think I should combine the lock & withdraw behaviors because an agent can only do one or the other each timestep,
but any number of agents can do either on every timestep. the logic would pick random lockers then the withdrawers
cannot be in the list of lockers. eventually, who and why an ocean holder decides to lock or withdraw on any given
timestep can be determined by strategies, but they will still only be able to pick one of the two actions each
timestep.

the outputs are already nearly identical, but i think I can just pass a dummy value for "duration" for any withdraw actions
!!!!!!!!!!!!!!!!!!!
'''

def behavior_move_ocean(timestep: int, oceanholders: dict, veaccounts: dict, minlock: int, maxlock: int) -> Dict[srt, list(float, int, str)]:
    # logic to determine which ocean holder agents lock ocean
    # current logic: every X timesteps, an ocean holder with positive ocean balance locks X ocean for Y days.
    #                From all ocean holders with positive balance, lock a random amt (or all if balance < random amt) for Y days
    if timestep % 20 == 0:
        action_lock = 'lock'
        valid_locking_agents = [key for key in oceanholders.keys() if oceanholders[key]['oceanbalance'] > 0]
        selected_locking_agent = random.choice(valid_locking_agents)
        ocean_balance = oceanholders[selected_locking_agent]['oceanbalance']
        lock_amount = min(random.random(0.0,2*ocean_balance), ocean_balance) #max=2*balance so that we empty balance 50% of the time and don't lock tiny amounts
        lock_duration = random.random(minlock, maxlock)
        new_veaccount = uuid.uuid4()
    else:
        action_lock = 'lock'
        selected_locking_agent = '0'
        lock_amount = 0
        lock_duration = 0
        new_veaccount = '0'

    # Logic determines which agents withdraw their unlocked ocean. EXCLUDING any agent who is locking ocean.
    if timestep % 25 == 0:
        # iterate through all ocean holders with positive balance of unlocked tokens in a ve account
        action_withdraw = 'withdraw'
        valid_withdrawing_agents = [key for key in oceanholders.keys() if [acct for acct in oceanholders[key]['veaccounts'] if veaccounts[acct]['unlocked'] > 0] in oceanholders[key]['veaccounts'] and key not in selected_locking_agents]
        selected_withdrawing_agent = random.choice(valid_withdrawing_agents)

        valid_veaccount = [acct for acct in oceanholders[selected_withdrawing_agent]['veaccounts'] if veaccounts[acct]['unlocked'] > 0]
        random_veaccount = random.choice(valid_veaccount)

        unlocked_balance = veaccounts[random_veaccount]['unlocked']
        withdraw_amount = min(random.random(0.0, 2*unlocked_balance), unlocked_balance) #max=2*balance so that we empty balance 50% of the time and don't leave tiny amounts
        withdraw_duration = 0 #n/a
    else:
        action_withdraw = 'withdraw'
        selected_withdrawing_agent = '0'
        withdraw_amount = 0
        withdraw_duration = 0
        existing_veaccount = '0'

    actions = action_lock + action_withdraw
    acting_agents = selected_locking_agent + selected_withdrawing_agent
    ocean_amounts = lock_amount + withdraw_amount
    durations = lock_duration + withdraw_duration
    veaccounts = new_veaccount + existing_veaccount

    return {acting_agents, (actions, ocean_amounts, durations, veaccounts)}