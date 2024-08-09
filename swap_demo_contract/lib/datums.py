"""
Datums implementation
To gain a better understanding of the Datum Standard structure, we recommend
visiting: https://github.com/Charli3-Official/oracle-datum-lib
and
https://docs.charli3.io/charli3s-documentation/oracle-feeds-datum-standard
"""

from dataclasses import dataclass

from pycardano import PlutusData
from pycardano.serialization import IndefiniteList

# ------------------------------#
#         Network Feed          #
# ------------------------------#


# Network feed
@dataclass
class PriceData(PlutusData):
    """Represents cip oracle datum PriceMap(Tag +2)"""

    CONSTR_ID = 2
    price_map: dict

    def get_price(self) -> int:
        """get price from price map"""
        return self.price_map[0]

    def get_timestamp(self) -> int:
        """get timestamp of the feed"""
        return self.price_map[1]

    def get_expiry(self) -> int:
        """get expiry of the feed"""
        return self.price_map[2]


@dataclass
class GenericData(PlutusData):
    """Oracle Datum"""

    CONSTR_ID = 0
    price_data: PriceData


# ------------------------------#
#     Network Configurations    #
# ------------------------------#


@dataclass
class OraclePlatform(PlutusData):
    """Oracle Platform parameters"""

    CONSTR_ID = 0
    pmultisig_pkhs: IndefiniteList  # Allowed pkhs for platform authorization
    pmultisig_threshold: int  # required number of signatories for authorization


@dataclass
class PriceRewards(PlutusData):
    """Node Fee parameters"""

    CONSTR_ID = 0
    node_fee: int  # Individual node reward for aggregation participation.
    aggregate_fee: int  # Node compensatoin for execution of the
    # aggregation transaction.
    platform_fee: int  # Platform compensation for maintenance systems.


@dataclass
class OracleSettings(PlutusData):
    """Oracle Settings parameters"""

    CONSTR_ID = 0
    os_node_list: IndefiniteList  # The list of autorized nodes'
    # public key hashes
    os_updated_nodes: int  # The percentage of nodes needed for aggregation
    os_updated_node_time: int  # The max time since last node update for
    # aggregation (in milliseconds)
    os_aggregate_time: int  # The min time since last aggregation for
    # calculating a new one (in milliseconds)
    os_aggregate_change: int  # The percentage of change between last
    # aggregated value and the new one
    os_minimum_deposit: int  # Minimum value required for topping up the
    # aggregate UTxO (1*10^9).
    os_aggregate_valid_range: int  # Valid time window to execute the
    # aggregate transaction (600000, 10min)
    os_node_fee_price: PriceRewards  # Rewards
    os_iqr_multiplier: int  # Threshold setting 1 for Consensus:
    # Interquartile Range (0 - N).
    os_divergence: int  # Threshold setting 2 for Consensus:
    # Divergence in Percentage
    os_platform: OraclePlatform  # Oracle platform entity


@dataclass
class AggState(PlutusData):
    """Agg State parameters"""

    CONSTR_ID = 0
    ag_settings: OracleSettings


@dataclass
class AggDatum(PlutusData):
    """Agg Datum"""

    CONSTR_ID = 2
    aggstate: AggState


@dataclass
class Nothing(PlutusData):
    CONSTR_ID = 1
