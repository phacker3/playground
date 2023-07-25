import sys
#sys.path.append("C:/Users/Surface/Documents/repos/playground")
sys.path.append("/home/peterhacker/Documents/phRepo/playground")

from Oceanmodel.policy_ve import *
from Oceanmodel.stateupdates_ve import *
from Oceanmodel.agents_ve import *
from Oceanmodel.behavior_ve import *

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


MONTE_CARLO_RUNS = 4#20
sim_length = 832 # 8 years

#seeds = [np.random.RandomState(i) for i in range(MONTE_CARLO_RUNS)]
#print(f"SEEDS: {seeds}")


initial_values = {
    'initial_data_assets': 100,
    'initial_token_supply': 1.41e9,
    'ocean_L1_allocation': 215.73e6,
    'datafarming_allocation': 503.4e6,
    'ocean_other_allocation': 0.0,
    'unlocked_supply': 434026836,
    'initial_DCV': 1000000, # CHANGE IT IN behavior_ve.py too!!!
    'initial_locked_pct': 0.03,
}



initial_assets = initialize_agent_data_asset(initial_values['initial_data_assets'], initial_values['initial_DCV'])

initial_state = {
    've_accounts': {},
    'votes': {key: 0.0 for key in initial_assets.keys()},
    'data_assets': initial_assets,
    'ocean_unlocked_supply': initial_values['unlocked_supply'],
    'ocean_treasury': initial_values['datafarming_allocation'],
    'rewards_distributed_df_active': 0,
    'rewards_distributed_df_passive': 0,
    'rewards_distributed_fees': 0,
    'rewards_pool_fees': 0,
    'distribution_schedule': np.array(pd.read_csv('distribution_schedule.txt', sep='\t', dtype=int)), # 482124587
}

system_params = {
    'vecontract_minlock': [1],
    'vecontract_maxlock': [4*52],
    'datafarming_active_share': [0.5],
    'datafarming_max_assets_n': [100],
    'datafarming_yield_cap': [0.015717], # Weekly Percent Yield needs to be 1.5717%., for max APY of 125%
    'protocol_revenue_community_share': [0.5],
    'protocol_transaction_fee': [0.001],
    'revenue_burn_pct': [0.5],
    'dcv_growth_rate': [0.1],
    'lock_pct_growth_rate': [0.03],
    'lock_pct_max': [0.85],
}

partial_state_update_blocks = [
    { # lock/vote/consume behaviors & allocate to rewards pools
        'policies': {
            'p_lock': p_lock,
            'p_vote': p_vote,
            'p_consume_data': p_data_asset_consumed,
        },
        'variables':{
            've_accounts': s_new_ve_accounts,
            'votes': s_votes,
            'data_assets': s_data_asset_consumed,
            'ocean_unlocked_supply': s_ocean_circ,
            'rewards_pool_fees': s_protocol_fees_pool
        }
    },
    { # distribute rewards
        'policies': {
            'p_active_rewards': p_active_rewards,
            'p_passive_and_fee_rewards':p_passive_and_fee_rewards
        },
        'variables':{
            'rewards_distributed_df_active': s_rewards_active,
            'rewards_distributed_df_passive': s_rewards_passive,
            'rewards_distributed_fees': s_rewards_fees,
            'ocean_treasury': s_treasury_ocean,
            'rewards_pool_fees': s_protocol_fees_pool,
            'ocean_unlocked_supply': s_ocean_circ,
        }
    },
    { # rebalance ve accounts
        'policies': {
            'p_rebalance': p_rebalance,
        },
        'variables':{
            've_accounts': s_rebalance_ve_accounts,
            'ocean_unlocked_supply': s_ocean_circ,
        }
    }
]


## generate behaviors:
## lock behaviors
#behavior_lock = b.behavior_lock(MONTE_CARLO_RUNS
#                                , sim_length
#                                , initial_values['initial_token_supply'] - initial_values['datafarming_allocation']
#                                , system_params['vecontract_minlock']
#                                , system_params['vecontract_maxlock'])
## vote behaviors
#behavior_vote = b.behavior_vote(MONTE_CARLO_RUNS
#                                , sim_length, initial_assets)
## consume behaviors
#behavior_consume_data = b.behavior_consume_data(MONTE_CARLO_RUNS
#                                                , sim_length
#                                                , initial_assets
#                                                , initial_values['initial_DCV'])



sim_config = config_sim({
    "N": MONTE_CARLO_RUNS,
    "T": range(sim_length),
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