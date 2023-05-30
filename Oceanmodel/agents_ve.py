from dataclasses import dataclass
from typing import *
import uuid

@dataclass
class oceanholder:
    #wallet: str
    oceanbalance: float
    veaccounts: list(str)

class veaccount:
    initialocean: float
    lockduration: int
    lockperiodstart: int
    locked: float
    unlocked: float
    withdrawn: float
    vebalance: float
    votepercent: Dict[int, float]

class dataasset:
    #assetID: int
    dataconsumevolume: int
    veallocation: float


def initialize_agent_oceanholder(n_oceanholders, token_supply) -> Dict(str, oceanholder):
    agents_oceanholder = {}

    for i in range(n_oceanholders):
        oceanbalance = token_supply / n_oceanholders
        veaccounts = {}
        
        agent = oceanholder(oceanbalance=oceanbalance, veaccounts=veaccounts)

        agents_oceanholder = agents_oceanholder[uuid.uuid4(), agent]
    
    return agents_oceanholder

def initialize_agent_data_asset(n_data_assets) -> Dict(str, dataasset):
    agents_data_asset = {}

    for i in range(n_data_assets):
        dcv = 0
        veallocation = 0.0
        
        agent = dataasset(dataconsumevolume=dcv, veallocation=veallocation)

        agents_data_asset = agents_data_asset[uuid.uuid4(), agent]
    
    return agents_data_asset

def initialize_agent_veaccount() -> Dict(str, veaccount):
    agents_veaccount = {}
    return agents_veaccount

# DONT THINK THIS WOULD WORK because the data classes are different
#def generate_agents(initial_ocean_holders, initial_data_assets, initial_token_supply) -> Dict(str, ):
#    agents_all = []
#    agents_oceanholder = initialize_agent_oceanholder(initial_ocean_holders, initial_token_supply),
#    agents_data_asset = initialize_agent_data_asset(initial_data_assets),
#    agents_veaccount = initialize_agent_veaccount()
#
#    agents_all.update(agents_oceanholder)
#    agents_all.update(agents_data_asset)
#    agents_all.update(agents_veaccount)
#
#    return agents_all
