from dataclasses import dataclass
from typing import *
import uuid

@dataclass
class veaccount:
    id: uuid.UUID
    initialocean: float
    lockduration: int
    lockperiodstart: int
    locked: float
    unlocked: float
    withdrawn: float
    vebalance: float
    votepercent: Dict[int, float]

class oceanholder:
    id: uuid.UUID
    oceanbalance: float
    veaccounts: List[veaccount]
    #veaccounts: Dict[uuid.UUID, str]

class dataasset:
    id: uuid.UUID
    dataconsumevolume: int
    veallocation: float


def initialize_agent_oceanholder(n_oceanholders, token_supply) -> Dict[str, oceanholder]:
    agents_oceanholder = {}

    for i in range(n_oceanholders):
        oceanbalance = token_supply / n_oceanholders
        veaccounts = []
        
        agent = oceanholder()
        
        agent.id=uuid.uuid4()
        agent.oceanbalance=oceanbalance
        agent.veaccounts=veaccounts

        agents_oceanholder[str(agent.id)] = agent
    
    return agents_oceanholder

def initialize_agent_data_asset(n_data_assets) -> Dict[str, dataasset]:
    agents_data_asset = {}

    for i in range(n_data_assets):
        dcv = 0
        veallocation = 0.0
        
        agent = dataasset()

        agent.id=uuid.uuid4()
        agent.dataconsumevolume=dcv
        agent.veallocation=veallocation

        agents_data_asset[str(agent.id)] = agent
    
    return agents_data_asset

def initialize_agent_veaccount() -> Dict[str, veaccount]:
    agents_veaccount = {}
    return agents_veaccount

def create_new_agent_veaccount(amount, duration, timestamp) -> veaccount:
    newagent = veaccount(
                        id=uuid.uuid4(),
                        initialocean=amount,
                        lockduration=duration,
                        lockperiodstart=timestamp,
                        locked=amount,
                        unlocked=0.0,
                        withdrawn=0.0,
                        vebalance=0.0,
                        votepercent={})
    

    #newagent.id=uuid.uuid4()
    #newagent.initialocean=amount
    #newagent.lockduration=duration
    #newagent.lockperiodstart=timestamp
    #newagent.locked=amount
    #newagent.unlocked=0.0
    #newagent.withdrawn=0.0
    #newagent.vebalance=0.0
    #newagent.votepercent={}

    return newagent

# DONT THINK THIS WOULD WORK because the data classes are different
#def generate_agents(initial_ocean_holders, initial_data_assets, initial_token_supply) -> dict(str, ):
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
