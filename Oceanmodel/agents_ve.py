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
    votepercent: Dict[uuid.UUID, float]

@dataclass
class oceanholder:
    id: uuid.UUID
    oceanbalance: float
    veaccounts: Dict[uuid.UUID, veaccount]

@dataclass
class dataasset:
    id: uuid.UUID
    dataconsumevolume: int
    veallocation: float

@dataclass
class dataassetholder:
    id: uuid.UUID
    dataassets: Dict[uuid.UUID, dataasset]


def initialize_agent_oceanholder(n_oceanholders, token_supply) -> Dict[str, oceanholder]:
    agents_oceanholder = {}

    for i in range(n_oceanholders):        
        agent = oceanholder(
                            id=uuid.uuid4(),
                            oceanbalance=token_supply / n_oceanholders,
                            veaccounts={}
                            )
        

        agents_oceanholder[str(agent.id)] = agent
    
    return agents_oceanholder

#def initialize_agent_veaccount() -> Dict[str, veaccount]:
#    agents_veaccount = {}
#    #dummyacct = veaccount(
#    #                    id='0',
#    #                    initialocean=0.0,
#    #                    lockduration=0,
#    #                    lockperiodstart=0,
#    #                    locked=0.0,
#    #                    unlocked=0.0,
#    #                    withdrawn=0.0,
#    #                    vebalance=0.0,
#    #                    votepercent={})
#    #
#    #agents_veaccount[str(dummyacct.id)] = dummyacct
#
#    return agents_veaccount

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

#def initialize_agent_data_asset(n_data_assets) -> Dict[str, dataasset]:
#    agents_data_asset = {}
#
#    for i in range(n_data_assets):
#        
#        agent = dataasset(
#                          id=uuid.uuid4(),
#                          dataconsumevolume=0,
#                          veallocation=0.0
#                         )
#        agents_data_asset[str(agent.id)] = agent
#    return agents_data_asset