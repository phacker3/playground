# at a given timestep, initialize a veOcean account by locking ocean
from typing import Tuple

def behavior_lockocean(timestep) -> Tuple[float, int]:
    if timestep == 5:
        amount = 100.0 # lock 100 Ocean
        duration = 1*52*7 # lock for 1 years
    else:
        amount = 0
        duration = 0
    return amount, duration
        
# at a given timestep, set the allocation percent for a data asset
def behavior_vote(timestep) -> Tuple[int, float]:
#def behavior_vote(timestep) -> float:
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
    #return vote

# at a given timestep, initiate a withdraw of unlocked ocean
def behavior_withdraw(timestep):
    if timestep == 150:
        amount = 20 # withdraw 5 unlocked ocean
    else:
        amount = 0
    return amount