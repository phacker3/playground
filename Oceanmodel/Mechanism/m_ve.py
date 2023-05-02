# the functions that output new invidivual state or stateful metric



def lockocean(amount, time):
    locked = amount
    duration = time
    return locked, duration

def withdrawocean(amount):
    withdraw_amount = amount
    return withdraw_amount

def sendocean(amt_sent):
    current_balance -= amt_sent
    return current_balance

def vebalance(starting_amount, duration, current_time, starting_time, maximum_lock):
    vebal = starting_amount * ((duration - (current_time - starting_time)) / maximum_lock)
    return vebal

def vote(asset, percent):
    assetnum = asset
    pct = percent
    return assetnum, pct
