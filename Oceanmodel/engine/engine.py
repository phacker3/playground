import sys
#sys.path.append("C:/Users/Surface/Documents/repos/playground")
sys.path.append("/home/peterhacker/Documents/phRepo/playground")

from Oceanmodel.Policy.p_ve import *
from Oceanmodel.StateUpdates.s_ve import *

import pandas as pd

# cadCAD configuration module
from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment

# cadCAD simulation engine modules
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor

from cadCAD import configs
del configs[:] # Clear any prior configs

experiment = Experiment()

initial_state = {
    'systime': 0,
    'oceanholder_oceanbalance': 200.0,
    'veaccount_1_initialocean': 0.0,
    'veaccount_1_lockduration': 0.0,
    'veaccount_1_lockperiodstart': 0,
    'veaccount_1_locked': 0.0,
    'veaccount_1_unlocked': 0.0,
    'veaccount_1_withdrawn': 0.0,
    'veaccount_1_vebalance': 0.0,
    'veaccount_1_asset_1_votepercent': 0.0,
    'asset_1_veallocation': 0.0
}   

system_params = {
    'vecontract_maxlock': [4*52*7]
}

partial_state_update_blocks = [ # note that #aggvotes needs to run AFTER veoceanbalance
    {
        'policies': {
            'new_account_duration': p_set_veaccount_params_duration,
            'new_locked_ocean': p_lock_ocean,
            'new_starting_timestep': p_set_veaccount_params_timestamp,
            'new_withdrawn_ocean': p_withdraw_ocean,
            'vote_data_asset': p_set_vote_data_asset,
            'vote_percent': p_set_vote_percent
        },
        # State variables
        'variables': {
            'veaccount_1_lockduration': s_lockedocean_duration,
            'oceanholder_oceanbalance':s_oceanholderbalance,
            'veaccount_1_locked':s_lock_ocean,
            'veaccount_1_initialocean':s_lockedocean_initialamount,
            'veaccount_1_lockperiodstart':s_lockedocean_starttimestamp,
            'veaccount_1_withdrawn': s_withdrawnocean,
            'veaccount_1_asset_1_votepercent':s_data_asset_pct
        }
    },
    {
        'policies': {
            'total_unlocked': p_rebalance_unlocked_ocean,
            'total_veocean_balance': p_rebalance_veocean
        },
        # State variables
        'variables': {
            'veaccount_1_unlocked': s_unlockedocean,
            'veaccount_1_vebalance': s_veocean_balance
        }
    },
    {
        'policies': {
            'rebalancedocean_locked': p_rebalance_locked_ocean,
            'data_asset_1_votes': p_aggregate_votes
        },
        # State variables
        'variables': {
            'veaccount_1_locked': s_locked_ocean,
            'asset_1_veallocation': s_aggvotes
        }
    }
    
]

sim_config = config_sim({
    "N": 1,
    "T": range(1460), #4 years
    "M": system_params
})

experiment.append_configs(
    initial_state = initial_state,
    partial_state_update_blocks = partial_state_update_blocks,
    sim_configs = sim_config
)

exec_context = ExecutionContext()

simulation = Executor(exec_context=exec_context, configs=configs)

raw_result, tensor_field, sessions = simulation.execute()

simulation_result = pd.DataFrame(raw_result)

#print(simulation_result.head())