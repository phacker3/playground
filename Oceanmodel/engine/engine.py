import ..Policy.p_ve as p
import ..StateUpdates.s_ve as s

import pandas as pd

# cadCAD configuration modules
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
    'veaccount_1_asset_1_vebalance': 0.0,
    'asset_1_veallocation': 0.0
}   

system_params = {
    'vecontract_maxlock': [4*52]
}

partial_state_update_blocks = [ # note that #aggvotes needs to run AFTER veoceanbalance
    {
        'policies': {
            'set_duration': p.p_set_veaccount_params_duration,
            'lock': p.p_lock_ocean,
            'set_timestamp': p.p_set_veaccount_params_timestamp,
            'withdrawn': p.p_withdraw_ocean,
            'vote_asset': p.p_set_vote_data_asset,
            'vote_pct': p.p_set_vote_percent
        },
        # State variables
        'variables': {
            'duration': s.s_lockedocean_duration,
            'oceanholder':s.s_oceanholderbalance,
            'locked':s.s_lockedocean,
            'initiallocked':s.s_lockedocean_initialamount,
            'lockedtimestamp':s.s_lockedocean_starttimestamp,
            'withdrawn': s.s_withdrawnocean,
            'votes':s.s_data_asset_pct
        }
    },
    {
        'policies': {
            'rebalance_unlocked': p.p_rebalance_unlocked_ocean,
            'rebalance_veocean': p.p_rebalance_veocean
        },
        # State variables
        'variables': {
            'unlocked': s.s_unlockedocean,
            'veocean': s.s_veocean_balance
        }
    },
    {
        'policies': {
            'rebalance_locked': p.p_rebalance_locked_ocean,
            'aggregatevotes': p.p_aggregate_votes
        },
        # State variables
        'variables': {
            'locked': s.s_lockedocean,
            'updatevotes': s.s_aggvotes
        }
    }
    
]

sim_config = config_sim({
    "N": 1,
    "T": range(250),
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

print(simulation_result.head())