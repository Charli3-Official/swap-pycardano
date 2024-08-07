import argparse
import yaml
import ogmios
import sys
import cbor2
import os

from datetime import datetime
from charli3_offchain_core.backend.kupo import KupoContext
from charli3_offchain_core.chain_query import ChainQuery
from pycardano import (
    Address,
    MultiAsset,
    Network,
    PlutusV2Script,
    plutus_script_hash,
    BlockFrostChainContext,
)


from . import wallet as w
from .mint import Mint
from .swap import SwapContract, Swap


def load_contracts_addresses():
    """Loads the contracts addresses"""
    configyaml = load_config()
    return (
        Address.from_primitive(configyaml.get("oracle_contract_address")),
        Address.from_primitive(configyaml.get("swap_contract_address")),
    )


def load_config():
    """Loads the YAML configuration file."""
    try:
        with open("config.yaml", "r", encoding="UTF-8") as config_yaml:
            return yaml.load(config_yaml, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("Configuration file not found.")
        sys.exit(1)


def validate_config(config, service, required_keys):
    """Validates that all required keys exist for a service configuration."""
    if service not in config or not all(
        key in config[service] for key in required_keys
    ):
        raise ValueError(f"Context for {service} not found or is incomplete.")


def context(args) -> ChainQuery:
    """Connection context"""
    blockfrost_context = None
    ogmios_context = None
    kupo_context = None

    configyaml = load_config()
    network = Network.TESTNET
    # if args.environment == "tesnet":
    #     network = Network.TESTNET
    # else:
    #     network = Network.MAINNET

    if args.service == "blockfrost":
        required_keys = ["project_id"]
        validate_config(configyaml, args.service, required_keys)

        blockfrost_context = BlockFrostChainContext(
            project_id=configyaml[args.service].get("project_id", ""),
            network=network,
            base_url=None,
        )
    elif args.service == "ogmios":
        required_keys = ["kupo_url", "ws_url"]
        validate_config(configyaml, args.service, required_keys)

        ogmios_ws_url = configyaml["ogmios"]["ws_url"]
        kupo_url = configyaml["ogmios"]["kupo_url"]

        _, ws_string = ogmios_ws_url.split("ws://")
        ws_url, port = ws_string.split(":")
        ogmios_context = ogmios.OgmiosChainContext(
            host=ws_url, port=int(port), network=network
        )

        kupo_context = KupoContext(kupo_url)

    return ChainQuery(
        blockfrost_context=blockfrost_context,
        ogmios_context=ogmios_context,
        kupo_context=kupo_context,
    )


oracle_address, swap_address = load_contracts_addresses()

swap_script_hash = swap_address.payment_part
# swap_script = context._get_script(str(swap_script_hash))

# if plutus_script_hash(swap_script) != swap_script_hash:
#     swap_script = PlutusV2Script(cbor2.dumps(swap_script))

# Reading minting script
#
current_dir = os.path.dirname(os.path.abspath(__file__))
mint_script_path = os.path.join(current_dir, "utils", "scripts", "mint_script.plutus")
with open(mint_script_path, "r") as f:
    script_hex = f.read()
    plutus_script_v2 = PlutusV2Script(cbor2.loads(bytes.fromhex(script_hex)))

# User payment key generation
# node_signing_key = PaymentSigningKey.generate()
# node_signing_key.save("node.skey")
# node_verification_key = PaymentVerificationKey.from_signing_key(node_signing_key)
# node_verification_key.save("node.vkey")

# Load user payment key
# extended_payment_skey = PaymentSigningKey.load("./credentials/node.skey")
# extended_payment_vkey = PaymentVerificationKey.load("./credentials/node.vkey")
#
# Load user payment key grom wallet file
extended_payment_skey = w.user_esk()

# User address wallet
user_address = w.user_address()

# Oracle feed NFT identity
oracle_nft = MultiAsset.from_primitive(
    {
        "8fe2ef24b3cc8882f01d9246479ef6c6fc24a6950b222c206907a8be": {
            b"InlineOracleFeed": 1
        }
    }
)

# Swap NFT identity
swap_nft = MultiAsset.from_primitive(
    {"38f143722e0a340027510587d81e49b90904c10fb8271eca13913cd6": {b"SWAP": 1}}
)

# tUSDT asset information
tUSDT = MultiAsset.from_primitive(
    {"c6f192a236596e2bbaac5900d67e9700dec7c77d9da626c98e0ab2ac": {b"USDT": 1}}
)

# swap instance
swap = Swap(swap_nft, tUSDT)

# ----------------------------- #
#         Parser Section        #
# ------------------------------#


def create_parser():
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="The swap python script is a demonstrative smart contract "
        "(Plutus v2) featuring the interaction with a Charli3's oracle. This "
        "script uses the inline oracle feed as reference input simulating the "
        "exchange rate between tADA and tUSDT to sell or buy assets from a swap "
        "contract in the test environment of preproduction. ",
        epilog="Copyrigth: (c) 2020 - 2024 Charli3",
    )

    # Create a subparser for each main choice
    subparser = parser.add_subparsers(dest="subparser")

    # Create a parser for the "trade" choice
    trade_subparser = subparser.add_parser(
        "trade",
        help="Call the trade transaction to exchange a user asset with another "
        "asset at the swap contract. Supported assets tADA and tUSDT.",
        description="Trade transaction to sell and buy tUSDT or tADA.",
    )

    # Create a subparser for each trade option
    subparser_trade_subparser = trade_subparser.add_subparsers(
        dest="subparser_trade_subparser"
    )

    tada_subparser_trade_subparser = subparser_trade_subparser.add_parser(
        "tADA", help="Toy ADA asset."
    )
    tada_subparser_trade_subparser.add_argument(
        "--amount",
        type=int,
        default=0,
        metavar="tLOVELACE",
        help="Amount of lovelace to trade.",
    )

    tusdt_subparser_trade_subparser = subparser_trade_subparser.add_parser(
        "tUSDT", help="Toy USDT asset."
    )
    tusdt_subparser_trade_subparser.add_argument(
        "--amount",
        type=int,
        default=0,
        metavar="tUSDT",
        help="Amount of tUSDT to trade.",
    )

    # Create a parser for the "user" choice
    user_parser = subparser.add_parser(
        "user",
        help="Obtain information about the wallet of the user who participate in "
        "the trade transaction.",
        description="User wallet information.",
    )
    user_parser.add_argument(
        "--liquidity",
        action="store_true",
        help="Print the amount of availables assets.",
    )

    user_parser.add_argument(
        "--address",
        action="store_true",
        help="Print the wallet address.",
    )

    # Create a parser for the "swap-contract" choice
    swap_contract_parser = subparser.add_parser(
        "swap-contract",
        help="Obtain information about the SWAP smart contract.",
        description="SWAP smart contract information.",
    )
    swap_contract_parser.add_argument(
        "--liquidity",
        action="store_true",
        help="Print the amount of availables assets.",
    )

    swap_contract_parser.add_argument(
        "--address",
        action="store_true",
        help="Print the swap contract address.",
    )

    swap_contract_parser.add_argument(
        "--add-liquidity",
        nargs=2,
        action="store",
        dest="addliquidity",
        metavar=("tUSDT", "tADA"),
        type=int,
        help="Add asset liquidity at swap UTXO.",
    )

    swap_contract_parser.add_argument(
        "--start-swap",
        dest="soracle",
        action="store_true",
        help="Generate a UTXO and mint an NFT at the specified swap contract address.",
    )

    # Create a parser for the "oracle-contract" choice
    oracle_contract_parser = subparser.add_parser(
        "oracle-contract",
        help="Obtain information about the ORACLE smart contract.",
        description="ORACLE smart contract information.",
    )
    oracle_contract_parser.add_argument(
        "--feed",
        action="store_true",
        help="Print the oracle feed (exchange rate) tUSDT/tADA.",
    )

    oracle_contract_parser.add_argument(
        "--address",
        action="store_true",
        help="Print the oracle contract address.",
    )
    return parser


# Parser command-line arguments
def display(args, context):
    if args.subparser == "trade" and args.subparser_trade_name == "tADA":
        swapInstance = SwapContract(
            context, oracle_nft, oracle_address, swap_address, swap
        )
        swapInstance.swap_B(
            args.amount,
            user_address,
            swap_address,
            swap_script,
            extended_payment_skey,
        )

    elif args.subparser_main_name == "trade" and args.subparser_trade_name == "tUSDT":
        swapInstance = SwapContract(
            context, oracle_nft, oracle_address, swap_address, swap
        )
        swapInstance.swap_A(
            args.amount,
            user_address,
            swap_address,
            swap_script,
            extended_payment_skey,
        )

    elif args.subparser_main_name == "user" and args.liquidity:
        swapInstance = SwapContract(
            context, oracle_nft, oracle_address, swap_address, swap
        )
        tlovelace = swapInstance.available_user_tlovelace(user_address)
        tUSDT = swapInstance.available_user_tusdt(user_address)
        print(
            f"""User wallet's liquidity:
        * {tlovelace // 1000000} tADA ({tlovelace} tlovelace).
        * {tUSDT} tUSDT."""
        )
    elif args.subparser_main_name == "user" and args.address:
        print(f"User's wallet address (Mnemonic): {w.user_address()}")
    elif args.subparser_main_name == "swap-contract" and args.liquidity:
        swapInstance = SwapContract(
            context, oracle_nft, oracle_address, swap_address, swap
        )
        tlovelace = swapInstance.get_swap_utxo().output.amount.coin
        tUSDT = swapInstance.add_asset_swap_amount(0)
        print(
            f"""Swap contract liquidity:
        * {tlovelace // 1000000} tADA ({tlovelace} tlovelace).
        * {tUSDT} tUSDT."""
        )
    elif args.subparser_main_name == "swap-contract" and args.address:
        print(f"Swap contract's address: {swap_address}")
    elif args.subparser_main_name == "swap-contract" and args.addliquidity:
        swapInstance = SwapContract(
            context, oracle_nft, oracle_address, swap_address, swap
        )
        swapInstance.add_liquidity(
            args.addliquidity[0],
            args.addliquidity[1],
            user_address,
            swap_address,
            swap_script,
            extended_payment_skey,
        )
    elif args.subparser_main_name == "swap-contract" and args.soracle:
        swap_utxo_nft = Mint(
            context, extended_payment_skey, user_address, swap_address, plutus_script_v2
        )
        swap_utxo_nft.mint_nft_with_script()

    elif args.subparser_main_name == "oracle-contract" and args.feed:
        swapInstance = SwapContract(
            context, oracle_nft, oracle_address, swap_address, swap
        )
        exchange = swapInstance.get_oracle_exchange_rate()
        generated_time = datetime.utcfromtimestamp(
            swapInstance.get_oracle_timestamp()
        ).strftime("%Y-%m-%d %H:%M:%S")
        expiration_time = datetime.utcfromtimestamp(
            swapInstance.get_oracle_expiration()
        ).strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"Oracle feed:\n* Exchange rate tADA/tUSDt {exchange/1000000}\n* "
            "Generated data at: {generated_time}\n* Expiration data "
            "at: {expiration_time}"
        )
    elif args.subparser_main_name == "oracle-contract" and args.address:
        print(f"Oracle contract's address: {oracle_address}")


def main():
    """main execution program"""
    parser = create_parser()
    args = parser.parse_args(None if sys.argv[1:] else ["-h"])
    ctx = context(args)
    display(args, ctx)


if __name__ == "__main__":
    main()