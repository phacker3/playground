import sys
#sys.path.append("C:/Users/Surface/Documents/repos/playground")
sys.path.append("/home/peterhacker/Documents/phRepo/playground")

from Oceanmodel.policy_ve import *
from Oceanmodel.stateupdates_ve import *
from Oceanmodel.agents_ve import *
from Oceanmodel.behavior_ve import *

import pandas as pd
import numpy as np
from copy import deepcopy
from itertools import product

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
    'min_accepted_apy_low': 0.05,
    'min_accepted_apy_high': 0.20
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


yield_list = list(map(lambda x: {'weekly_yield': (1+x)**(1/52)-1, 'apy': x}, np.arange(initial_values['min_accepted_apy_low'],initial_values['min_accepted_apy_high'],(initial_values['min_accepted_apy_high'] - initial_values['min_accepted_apy_low'])/5)))
weekly_lock_prob_list = list(np.arange(0.30, 0.81, 0.25))
weekly_vote_success_prob_list = list(np.arange(0.1, 0.61, 0.25))
weekly_consume_multiple_list = [1, 1.4] # for low/med/high dcv scenarios
lock_dur_list = [
    {'min_lock': 1, 'max_lock': 4*52}
    , {'min_lock': 1, 'max_lock': 2*52}
    , {'min_lock': 1*52, 'max_lock': 3*52}
    , {'min_lock': 2*52, 'max_lock': 4*52}
]

system_params = {
    'minlock_amt': [10e3],
    'maxlock_amt': [5e6],
    'lock_dur': lock_dur_list,
    'minlock_dur': [1],
    'maxlock_dur': [4*52],
    'min_weekly_dcv_amt': [100],
    'max_weekly_dcv_amt': [1000],
    'weekly_lock_prob': weekly_lock_prob_list,
    'weekly_vote_success_prob': weekly_vote_success_prob_list,
    'weekly_consume_prob': [1.0],#weekly_consume_prob_list,
    'weekly_consume_multiple': weekly_consume_multiple_list,
    'datafarming_active_share': [0.5],
    'datafarming_max_assets_n': [100],
    'datafarming_weekly_yield_cap': [0.015717], # Weekly Percent Yield needs to be 1.5717%., for max APY of 125%
    'datafarming_apy_cap': [1.25],
    'protocol_revenue_community_share': [0.5],
    'protocol_transaction_fee': [0.001],
    'revenue_burn_pct': [0.5],
    'dcv_growth_rate': [0.1],
    'min_accepted_yield': [0.0],#yield_list,
    'lock_supply_pct_cap': [0.85]
}

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

def create_par_sweep(sweep_dict: dict) -> dict:
    """This function takes a dictionary where key is parameter name
    and value is a list of all possible values for that parameter. It
    converts this into a dictionary with the same keys but with values
    that are the cartesian product of all the lists.

    Args:
        sweep_dict (dict): A dictionary of params and values to sweep over

    Returns:
        dict: A dictionary of cartesian product params
    """
    # Copy sweep_dict to avoid overwriting
    sweep_dict = deepcopy(sweep_dict)

    # Get the cartesian product
    sweeps = list(product(*sweep_dict.values()))

    # Assign values
    for kk, varname in enumerate(sweep_dict.keys()):
        sweep_dict[varname] = [x[kk] for x in sweeps]

    return sweep_dict

def generate_psubs_all() -> List[List[Dict[str, any]]]:

    locking = [p_lock_1, p_lock_2, p_lock_3] #L1 with V1/2, L2 with V3/4
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

def generate_psubs_LinearLocking_PerfectActivationVotingVolume() -> List[List[Dict[str, any]]]:

    locking = [p_lock_1]
    voting = [p_vote_5]
    consuming = [p_data_asset_consumed_1, p_data_asset_consumed_2, p_data_asset_consumed_3]

    psubs = []
    for l in locking:
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

def generate_psubs_LazyLocking_PerfectActivationVotingVolume() -> List[List[Dict[str, any]]]:

    locking = [p_lock_2]
    voting = [p_vote_5]
    consuming = [p_data_asset_consumed_1, p_data_asset_consumed_2, p_data_asset_consumed_3]

    psubs = []
    for l in locking:
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

def generate_psubs_SmartLocking_PerfectActivationVotingVolume() -> List[List[Dict[str, any]]]:

    locking = [p_lock_3]
    voting = [p_vote_5]
    consuming = [p_data_asset_consumed_1, p_data_asset_consumed_2, p_data_asset_consumed_3]

    psubs = []
    for l in locking:
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

def generate_psubs_stoch() -> List[List[Dict[str, any]]]:

    locking = [p_lock_stoch]
    voting = [p_vote_stoch]
    consuming = [p_data_asset_consumed_stoch]

    psubs = []
    for l in locking:
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

def generate_psubs_stoch_2() -> List[List[Dict[str, any]]]:

    locking = [p_lock_stoch]
    voting = [p_vote_stoch, p_vote_stoch_2]
    consuming = [p_data_asset_consumed_stoch, p_data_asset_consumed_stoch_2]

    psubs = []
    for l in locking:
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