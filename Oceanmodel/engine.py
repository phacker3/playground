import sys
#sys.path.append("C:/Users/Surface/Documents/repos/playground")
sys.path.append("/home/peterhacker/Documents/phRepo/playground")

from Oceanmodel.policy_ve import *
from Oceanmodel.stateupdates_ve import *
from Oceanmodel.agents_ve import *

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


initial_values = {
    'initial_ocean_holders': 1,
    'initial_data_assets': 1,
    'initial_token_supply': 1e6
}   

genesis_states = {
    'agents_oceanholder': initialize_agent_oceanholder(initial_values['initial_ocean_holders'], initial_values['initial_token_supply']),
    #'agents_data_asset': initialize_agent_data_asset(initial_values['initial_data_assets'])
    #'agents_veaccount': initialize_agent_veaccount()
}

initial_state = genesis_states

system_params = {
    'vecontract_minlock': [7],
    'vecontract_maxlock': [4*52*7]
}

partial_state_update_blocks = [
    {
        'policies': {
            'p_lock_withdraw': p_lock_withdraw
        },
        'variables':{
            'oceanholders': s_agents_oceanholder_lock_withdraw
        }
    },
    {
        'policies': {
            'p_rebalance': p_rebalance
        },
        'variables':{
            'oceanholders': s_agents_oceanholder_rebalance
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