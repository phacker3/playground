# at a given timestep, initialize a veOcean account by locking ocean

def behavior_lockocean(timestep):
    if timestep == 5:
        amount = 100.0 # lock 100 Ocean
        duration = 2*52 # lock for 2 years
    else:
        amount = 0
        duration = 0
    return amount, duration
        
# at a given timestep, set the allocation percent for a data asset
def behavior_vote(timestep):
    if timestep == 20:
        asset = 1
        vote = 0.25
    if timestep == 60:
        asset = 1
        vote = 0.4
    else:
        asset = 0
        vote = 0
    return asset, vote

# at a given timestep, initiate a withdraw of unlocked ocean
def behavior_withdraw(timestep):
    if timestep == 50:
        amount = 5 # withdraw 5 unlocked ocean
    else:
        amount = 0
    return amount