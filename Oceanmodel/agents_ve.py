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

@dataclass
class oceanholder:
    id: uuid.UUID
    oceanbalance: float
    veaccounts: Dict[uuid.UUID, veaccount]
    votepercent: Dict[uuid.UUID, float]

@dataclass
class dataasset:
    id: uuid.UUID
    dataconsumevolume: int
    veallocation: float


def initialize_agent_oceanholder(n_oceanholders, token_supply) -> Dict[str, oceanholder]:
    agents_oceanholder = {}
    for i in range(n_oceanholders):        
        agent = oceanholder(
                            id=uuid.uuid4(),
                            oceanbalance=token_supply / n_oceanholders,
                            veaccounts={},
                            votepercent={}
                            )
        agents_oceanholder[str(agent.id)] = agent
    return agents_oceanholder


def create_new_agent_veaccount(amount, duration, timestamp) -> veaccount:
    newagent = veaccount(
                        id=uuid.uuid4(),
                        initialocean=amount,
                        lockduration=duration,
                        lockperiodstart=timestamp,
                        locked=amount,
                        unlocked=0.0,
                        withdrawn=0.0,
                        vebalance=0.0)
    return newagent


def initialize_agent_data_asset(n_data_assets) -> Dict[str, dataasset]:
    agents_data_asset = {}
    for i in range(n_data_assets):
        agent = dataasset(
                          id=uuid.uuid4(),
                          dataconsumevolume=0,
                          veallocation=0.0
                         )
        agents_data_asset[str(agent.id)] = agent
    return agents_data_asset