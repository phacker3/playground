import sys
#sys.path.append("C:/Users/Surface/Documents/repos/playground")
sys.path.append("/home/peterhacker/Documents/phRepo/playground")

from Oceanmodel.policy_ve import *
from Oceanmodel.stateupdates_ve import *
from Oceanmodel.agents_ve import *

import pandas as pd
import numpy as np

# cadCAD configuration module
from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment

# cadCAD simulation engine modules
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor

from cadCAD import configs
del configs[:] # Clear any prior configs

experiment = Experiment()


MONTE_CARLO_RUNS = 1

#seeds = [np.randomseed(i) for i in range(MONTE_CARLO_RUNS)]


initial_values = {
    'initial_ocean_holders': 4,
    'initial_data_assets': 4,
    #'initial_token_supply': 1.41e9,
    'datafarming_allocation': 503.4e6
}


initialize_oceanholders = initialize_agent_oceanholder(initial_values['initial_ocean_holders'])
initialize_assets = initialize_agent_data_asset(initial_values['initial_data_assets'])
initialize_matrix = initialize_rewards_matrix(initialize_oceanholders, initialize_assets)
print(initialize_assets.keys())
print(initialize_matrix)

initial_state = {
    'agents_oceanholder': initialize_oceanholders,
    'agents_data_asset': initialize_assets,
    #'ocean_total_supply': initial_values['initial_token_supply'],
    'ocean_treasury': initial_values['datafarming_allocation'],
    'rewards_pool_df_active': 0,
    'rewards_pool_df_passive': 0,
    'rewards_pool_fees': 0,
    'distribution_schedule': np.array(pd.read_csv('distribution_schedule.txt', sep='\t', dtype=int)),
    'rewards_matrix': initialize_matrix
}

system_params = {
    'vecontract_minlock': [7],
    'vecontract_maxlock': [4*52*7],
    'datafarming_active_share': [0.5],
    'datafarming_max_assets_n': [100],
    'datafarming_yield_cap': [0.015717], # Weekly Percent Yield needs to be 1.5717%., for max APY of 125%
    'protocol_revenue_community_share': [0.5]
}

partial_state_update_blocks = [
    { # lock,vote,withdraw,consume behaviors & allocate to rewards pools
        'policies': {
            'p_lock_withdraw': p_lock_withdraw,
            'p_vote': p_vote,
            'p_release_ocean': p_release_ocean,
        },
        'variables':{
            'agents_oceanholder': s_agents_oceanholder_behaviors,
            'ocean_treasury': s_treasury_ocean,
            'rewards_pool_df_active': s_data_farming_active_pool,
            'rewards_pool_df_passive': s_data_farming_passive_pool
        }
    },
    { # distribute rewards
        'policies': {
            'p_active_rewards': p_active_rewards,
            'p_passive_and_fee_rewards':p_passive_and_fee_rewards
        },
        'variables':{
            'ocean_treasury': s_treasury_ocean,
            'rewards_pool_df_active': s_data_farming_active_pool,
            'rewards_pool_df_passive': s_data_farming_passive_pool,
            'rewards_pool_fees': s_protocol_fees_pool,
            'agents_oceanholder': s_oceanholder_rewards_function
        }
    },
    { # rebalance ve accounts
        'policies': {
            'p_rebalance': p_rebalance,
            'p_data_asset_consumed': p_data_asset_consumed
        },
        'variables':{
            'agents_oceanholder': s_agents_oceanholder_rebalance,
            'agents_data_asset': s_data_asset_consumed
        }
    },
    { # aggregate votes
        'policies': {
            'p_aggregate_votes': p_aggregate_votes,
            'p_rewards_matrix': p_rewards_matrix_snapshot
        },
        'variables':{
            'agents_data_asset': s_agents_data_asset_aggregate_votes,
            'rewards_matrix': s_rewards_matrix
        }
    }
]

sim_config = config_sim({
    "N": MONTE_CARLO_RUNS,
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