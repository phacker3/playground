from dataclasses import dataclass
from typing import *
import uuid
import numpy as np

@dataclass
class veaccount:
    id: uuid.UUID
    initialocean: float
    lockduration: int
    lockperiodstart: int
    locked: float
    vebalance: float

@dataclass
class dataasset:
    id: uuid.UUID
    dataconsumevolume: float

def create_new_agent_veaccount(amount, duration, timestamp, max_duration) -> veaccount:
    newagent = veaccount(
                        id=uuid.uuid4(),
                        initialocean=amount,
                        lockduration=duration,
                        lockperiodstart=timestamp,
                        locked=amount,
                        vebalance=amount*(duration - (timestamp - timestamp))/(max_duration))
    return newagent


def initialize_agent_data_asset(n_data_assets, initial_DCV) -> Dict[str, dataasset]:
    agents_data_asset = {}
    for i in range(n_data_assets):
        agent = dataasset(
                          id=uuid.uuid4(),
                          dataconsumevolume=0.0
                         )
        agents_data_asset[str(agent.id)] = agent

    dcv = initial_DCV
    assets_consumed = {}
    for asset in agents_data_asset.keys():
        assets_consumed[asset] = np.random.uniform(0.0,1.0)
    total_consumed = sum(assets_consumed.values())
    for asset in agents_data_asset.keys():
        assets_consumed[asset] = assets_consumed[asset]/total_consumed*dcv

    for asset in agents_data_asset.keys():
        agents_data_asset[asset].dataconsumevolume = assets_consumed[asset]

    return agents_data_asset