""" Type for IO
"""

from typing import TypedDict


class PostgresConfig(TypedDict):
    host: str
    user: str
    pwd: str
    port: int
    database: str


class CosmosConfig(TypedDict):
    host: str
    master_key: str
    database_id: str
    container_id: str


class EngineConfig(TypedDict):
    engine_type: str
    engine_conf: PostgresConfig | CosmosConfig
