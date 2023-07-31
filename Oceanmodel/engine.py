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

#seeds = [np.random.RandomState(i) for i in range(MONTE_CARLO_RUNS)]
#print(f"SEEDS: {seeds}")


initial_values = {
    'initial_data_assets': 100,
    'initial_token_supply': 1.41e9,
    'ocean_L1_allocation': 215.73e6,
    'datafarming_allocation': 503.4e6,
    'ocean_other_allocation': 0.0,
    'unlocked_supply': 434026836,
    'initial_DCV': 50000, # CHANGE IT IN behavior_ve.py too!!!
    'initial_locked_pct': 0.03, # CHANGE IT IN behavior_ve.py too!!!
    'min_accepted_apy': 0.1
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
    'datafarming_weekly_yield_cap': [0.015717], # Weekly Percent Yield needs to be 1.5717%., for max APY of 125%
    'datafarming_apy_cap': [1.25],
    'protocol_revenue_community_share': [0.5],
    'protocol_transaction_fee': [0.001],
    'revenue_burn_pct': [0.5],
    'dcv_growth_rate': [0.1],
    'min_accepted_weekly_yield': [(initial_values['min_accepted_apy'] + 1)**(1/52)-1], #annual! not weekly. weekly = (APY + 1)^(1/52)-1
    'min_accepted_apy': [initial_values['min_accepted_apy']],
    'lock_supply_pct_cap': [0.85],
}

#partial_state_update_blocks_behaviors_A = [
#    { # lock/vote/consume behaviors & allocate to rewards pools
#        'policies': {
#            'p_lock': p_lock_a,
#            'p_vote': p_vote,
#            'p_consume_data': p_data_asset_consumed,
#        },
#        'variables':{
#            've_accounts': s_new_ve_accounts,
#            'votes': s_votes,
#            'data_assets': s_data_asset_consumed,
#            'ocean_unlocked_supply': s_ocean_circ,
#            'rewards_pool_fees': s_protocol_fees_pool
#        }
#    },
#    { # distribute rewards
#        'policies': {
#            'p_active_rewards': p_active_rewards,
#            'p_passive_and_fee_rewards':p_passive_and_fee_rewards
#        },
#        'variables':{
#            'rewards_distributed_df_active': s_rewards_active,
#            'rewards_distributed_df_passive': s_rewards_passive,
#            'rewards_distributed_fees': s_rewards_fees,
#            'ocean_treasury': s_treasury_ocean,
#            'rewards_pool_fees': s_protocol_fees_pool,
#            'ocean_unlocked_supply': s_ocean_circ,
#        }
#    },
#    { # rebalance ve accounts
#        'policies': {
#            'p_rebalance': p_rebalance,
#        },
#        'variables':{
#            've_accounts': s_rebalance_ve_accounts,
#            'ocean_unlocked_supply': s_ocean_circ,
#        }
#    }
#]
#
#partial_state_update_blocks_behaviors_B = [
#    { # lock/vote/consume behaviors & allocate to rewards pools
#        'policies': {
#            'p_lock': p_lock_b,
#            'p_vote': p_vote,
#            'p_consume_data': p_data_asset_consumed,
#        },
#        'variables':{
#            've_accounts': s_new_ve_accounts,
#            'votes': s_votes,
#            'data_assets': s_data_asset_consumed,
#            'ocean_unlocked_supply': s_ocean_circ,
#            'rewards_pool_fees': s_protocol_fees_pool
#        }
#    },
#    { # distribute rewards
#        'policies': {
#            'p_active_rewards': p_active_rewards,
#            'p_passive_and_fee_rewards':p_passive_and_fee_rewards
#        },
#        'variables':{
#            'rewards_distributed_df_active': s_rewards_active,
#            'rewards_distributed_df_passive': s_rewards_passive,
#            'rewards_distributed_fees': s_rewards_fees,
#            'ocean_treasury': s_treasury_ocean,
#            'rewards_pool_fees': s_protocol_fees_pool,
#            'ocean_unlocked_supply': s_ocean_circ,
#        }
#    },
#    { # rebalance ve accounts
#        'policies': {
#            'p_rebalance': p_rebalance,
#        },
#        'variables':{
#            've_accounts': s_rebalance_ve_accounts,
#            'ocean_unlocked_supply': s_ocean_circ,
#        }
#    }
#]
#
#
#partial_state_update_blocks_behaviors_C = [
#    { # lock/vote/consume behaviors & allocate to rewards pools
#        'policies': {
#            'p_lock': p_lock_c,
#            'p_vote': p_vote_c,
#            'p_consume_data': p_data_asset_consumed,
#        },
#        'variables':{
#            've_accounts': s_new_ve_accounts,
#            'votes': s_votes,
#            'data_assets': s_data_asset_consumed,
#            'ocean_unlocked_supply': s_ocean_circ,
#            'rewards_pool_fees': s_protocol_fees_pool
#        }
#    },
#    { # distribute rewards
#        'policies': {
#            'p_active_rewards': p_active_rewards_c,
#            'p_passive_and_fee_rewards':p_passive_and_fee_rewards
#        },
#        'variables':{
#            'rewards_distributed_df_active': s_rewards_active,
#            'rewards_distributed_df_passive': s_rewards_passive,
#            'rewards_distributed_fees': s_rewards_fees,
#            'ocean_treasury': s_treasury_ocean,
#            'rewards_pool_fees': s_protocol_fees_pool,
#            'ocean_unlocked_supply': s_ocean_circ,
#        }
#    },
#    { # rebalance ve accounts
#        'policies': {
#            'p_rebalance': p_rebalance,
#        },
#        'variables':{
#            've_accounts': s_rebalance_ve_accounts,
#            'ocean_unlocked_supply': s_ocean_circ,
#        }
#    }
#]


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


def generate_psubs() -> List[List[Dict[str, any]]]:

    locking = [p_lock_1, p_lock_2] #L1 with V1/2, L2 with V3/4
    consuming = [p_data_asset_consumed_1, p_data_asset_consumed_2, p_data_asset_consumed_3]

    psubs = []
    for l in locking:
        if l == p_lock_1:
            voting = [p_vote_1, p_vote_2]
        else:
            voting = [p_vote_3, p_vote_4]
        for v in voting:
            for c in consuming:
                psubs.append([
                    { # lock/consume behaviors & allocate to rewards pools
                        'policies': {
                            'p_lock': l,
                            'p_consume': c
                        },
                        'variables':{
                            've_accounts': s_new_ve_accounts,
                            'data_assets': s_data_asset_consumed,
                            'ocean_unlocked_supply': s_ocean_circ,
                            'rewards_pool_fees': s_protocol_fees_pool
                        }
                    },
                    { # vote behavior
                        'policies': {
                            'p_vote': v
                        },
                        'variables':{
                            'votes': s_votes
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
                ])
                print(f"psub assumptions: Locking: {l.__name__}, Voting: {v.__name__}, Consumption: {c.__name__}")
    return psubs