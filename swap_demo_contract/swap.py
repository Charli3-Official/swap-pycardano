"""Swap Contract"""

from datetime import datetime

import pycardano as pyc
from charli3_offchain_core.chain_query import ChainQuery

from .lib.datums import GenericData
from .lib.redeemers import AddLiquidity, SwapA, SwapB


class Swap:
    """Class Swap for interact with the assets in the swap operation
    and identify the Swap's NFTs

    Attribures:
        swap_nft: The NFT identifier of the swap utxo
        coinA: Asset
    """

    def __init__(
        self,
        swap_nft: pyc.MultiAsset,
        coinA: pyc.MultiAsset,
    ) -> None:
        self.swap_nft = swap_nft
        self.coinA = coinA


class SwapContract:
    """SwapContact to interact with the swap smart contract

    Attributes:
        context: Blockfrost class
        oracle_nft: The NFT identifier of the oracle feed utxo
        oracle_addr: Address of the oracle contract
        swap_addr: Address of the swap contract
    """

    def __init__(
        self,
        chain_query: ChainQuery,
        oracle_nft: pyc.MultiAsset,
        oracle_addr: pyc.Address,
        swap_addr: pyc.Address,
        swap: Swap,
    ) -> None:
        self.chain_query = chain_query
        self.oracle_addr = oracle_addr
        self.swap_addr = swap_addr
        self.coin_precision = 1000000
        self.swap = swap
        self.oracle_nft = oracle_nft

    async def add_liquidity(
        self,
        amountA: int,
        amountB: int,
        user_address: pyc.Address,
        swap_address: pyc.Address,
        script: bytes,
        sk: pyc.PaymentSigningKey,
    ):

        swap_utxo = await self.get_swap_utxo()
        available_user_tADA = (
            await self.available_user_tlovelace(user_address) // 1000000
        )
        available_user_tUSDT = await self.available_user_tusdt(user_address)
        if available_user_tADA < amountB or available_user_tUSDT < amountA:
            print(
                f"""Error! The user's wallet  doesn't have enough liquidity!
            Available: {available_user_tUSDT} tUSDT, {available_user_tADA} tADA"""
            )
        else:
            updated_swap_multi_asset, updated_swap_total_amount = (
                await self.add_asset_swap(amountA)
            )

            updated_amountB_for_swap_utxo = (
                swap_utxo.output.amount.coin + amountB * 1000000
            )

            swap_redeemer = pyc.Redeemer(AddLiquidity())

            swap_value = pyc.transaction.Value(
                coin=updated_amountB_for_swap_utxo,
                multi_asset=updated_swap_multi_asset,
            )

            updated_swap_utxo = pyc.TransactionOutput(
                address=swap_address, amount=swap_value, datum=pyc.Unit()
            )

            builder = pyc.TransactionBuilder(self.chain_query.context)
            (
                builder.add_script_input(
                    utxo=swap_utxo,
                    script=script,
                    redeemer=swap_redeemer,
                )
                .add_input_address(user_address)
                .add_output(updated_swap_utxo)
            )

            await self.chain_query.submit_tx_builder(builder, sk, user_address)

            print("Updated swap contract liquidity:")
            print(
                f"- {updated_amountB_for_swap_utxo // 1000000} tADA ({updated_amountB_for_swap_utxo} tlovelaces)"
            )
            print(f"- {updated_swap_total_amount} tUSDT.")

    async def swap_A(
        self,
        amountA: int,
        user_address: pyc.Address,
        swap_address: pyc.Address,
        script: bytes,
        sk: pyc.PaymentSigningKey,
    ):
        """Exchange of asset A  with B"""
        oracle_feed_utxo = await self.get_oracle_utxo()
        swap_utxo = await self.get_swap_utxo()
        amountB = await self.swap_a_with_b(amountA)
        amountB_precision = amountB * self.coin_precision

        swap_amountB_tADA = swap_utxo.output.amount.coin // 1000000
        user_amountB_tUSDT = await self.available_user_tusdt(user_address)

        if amountB < 1:
            print(
                f"The minimum sale quantity of tADA is 1. Current value {amountB} tADA."
            )

        elif amountB > swap_amountB_tADA:
            print(f"Error! The user's wallet doesn't have enough liquidity!")
            print(f"Available: {swap_amountB_tADA} tUSDT.")
        elif amountA > user_amountB_tUSDT:
            print(f"Error! The user's wallet doesn't have enough liquidity!")
            print(f"Available: {user_amountB_tUSDT} tUSDT.")
        else:
            swap_redeemer = pyc.Redeemer(SwapA(amountA))

            amount_for_the_user = pyc.transaction.Value(coin=amountB_precision)

            new_output_utxo_user = pyc.TransactionOutput(
                address=user_address, amount=amount_for_the_user
            )

            # swap utxo
            # TODO change units to ada instead of lovelace
            updated_amountB_for_swap_utxo = swap_utxo.output.amount.coin - amountB

            updated_swap_multi_asset, updated_swap_total_amount = (
                await self.add_asset_swap(amountA)
            )
            amount_swap = pyc.transaction.Value(
                coin=updated_amountB_for_swap_utxo,
                multi_asset=updated_swap_multi_asset,
            )

            new_output_swap = pyc.TransactionOutput(
                address=swap_address, amount=amount_swap, datum=pyc.Unit()
            )

            builder = pyc.TransactionBuilder(self.chain_query.context)
            (
                builder.add_script_input(
                    utxo=swap_utxo, script=script, redeemer=swap_redeemer
                )
                .add_input_address(user_address)
                .add_output(new_output_utxo_user)
                .add_output(new_output_swap)
                .reference_inputs.add(oracle_feed_utxo.input)
            )

            print(f"Exchanging {amountA} lovelace for {amountB} tADA.")
            await self.chain_query.submit_tx_builder(builder, sk, user_address)

            print("Updated swap contract liquidity:")
            print(f"- {updated_amountB_for_swap_utxo} tlovelaces.")
            print(f"- {updated_swap_total_amount} tUSDT.")

    async def swap_B(
        self,
        amountB: int,
        user_address: pyc.Address,
        swap_address: pyc.Address,
        script: bytes,
        sk: pyc.PaymentSigningKey,
    ):
        """Exchange of asset B  with A"""
        oracle_feed_utxo = await self.get_oracle_utxo()
        swap_utxo = await self.get_swap_utxo()
        amountA = await self.swap_b_with_a(amountB)
        available_user_tADA = (
            await self.available_user_tlovelace(user_address) // 1000000
        )

        available_swap_tusdt = await self.decrease_asset_swap_amount(0)
        if amountA < 1:
            print(
                f"The minimum sale quantity of tUSDT is 1. Current value {amountA} tUSDT."
            )
        elif amountB > available_user_tADA:
            print(
                f"""Error! The user's wallet doesn't have enough liquidity!
            Available: {available_user_tADA} tADA."""
            )
        elif amountA > available_swap_tusdt:
            print(
                f"""Error! The swap contract doesn't have enough liquidity!
            Available: {available_swap_tusdt} tUSDT."""
            )
        else:
            swap_redeemer = pyc.Redeemer(SwapB(amountB))

            multi_asset_for_the_user = await self.take_multi_asset_user(amountA)

            # Add the minimum lovelace amount to the user value
            amount_for_the_user = pyc.transaction.Value(
                coin=2000000, multi_asset=multi_asset_for_the_user
            )

            # Add the value to the user UTXO
            new_output_utxo_user = pyc.TransactionOutput(
                address=user_address, amount=amount_for_the_user
            )

            amountB_at_swap_utxo = swap_utxo.output.amount.coin
            updated_amountB_for_swap_utxo = amountB_at_swap_utxo + (amountB * 1000000)

            updated_masset_for_swap_utxo = await self.decrease_asset_swap(amountA)
            updated_masset_amount_for_swap_utxo = await self.decrease_asset_swap_amount(
                amountA
            )

            amount_swap = pyc.transaction.Value(
                coin=updated_amountB_for_swap_utxo,
                multi_asset=updated_masset_for_swap_utxo,
            )

            new_output_swap = pyc.TransactionOutput(
                address=swap_address, amount=amount_swap, datum=pyc.Unit()
            )

            builder = pyc.TransactionBuilder(self.chain_query.context)
            (
                builder.add_script_input(
                    utxo=swap_utxo,
                    script=script,
                    redeemer=swap_redeemer,
                )
                .add_input_address(user_address)
                .add_output(new_output_utxo_user)
                .add_output(new_output_swap)
                .reference_inputs.add(oracle_feed_utxo.input)
            )

            print(f"Exchanging {amountB} tADA for {amountA} tUSDT.")
            await self.chain_query.submit_tx_builder(builder, sk, user_address)
            # await self.submit_tx_builder(builder, sk, user_address)
            print("Updated swap contract liquidity:")
            print(
                f"- {updated_amountB_for_swap_utxo // 1000000 } tADA ({updated_amountB_for_swap_utxo} tlovelaces)."
            )
            print(f"- {updated_masset_amount_for_swap_utxo} tUSDT.")

    async def swap_b_with_a(self, amount_b: int) -> int:
        """Operation for swaping coin B with A"""
        exchange_rate_price = await self.get_oracle_exchange_rate()
        print(
            f"Oracle exchange rate: {exchange_rate_price / self.coin_precision} tUSDT/tADA (A/B)"
        )
        return (amount_b * self.coin_precision) // exchange_rate_price

    async def swap_a_with_b(self, amount_a: int) -> int:
        """Operation for swaping coin A with B"""
        exchange_rate_price = await self.get_oracle_exchange_rate()
        print(
            f"Oracle exchange rate: {exchange_rate_price / self.coin_precision} tUSDT/tADA (A/B)"
        )
        return (amount_a * exchange_rate_price) // self.coin_precision

    def format_timestamp(self, timestamp):
        """Convert epoch to humnan"""
        return datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")

    async def get_oracle_exchange_rate(self) -> int:
        """Get the oracle's feed exchange rate"""
        price = 0
        oracle_feed_utxo = await self.get_oracle_utxo()

        if oracle_feed_utxo.output.datum and not isinstance(
            oracle_feed_utxo.output.datum, GenericData
        ):
            if oracle_feed_utxo.output.datum.cbor:
                oracle_inline_datum = GenericData.from_cbor(
                    oracle_feed_utxo.output.datum.cbor
                )
                price = oracle_inline_datum.price_data.get_price()

        return price

    async def get_oracle_timestamp(self) -> int:
        """Get the oracle's feed exchange rate"""
        oracle_feed_utxo = await self.get_oracle_utxo()
        oracle_inline_datum: GenericData = GenericData.from_cbor(
            oracle_feed_utxo.output.datum.cbor
        )
        return oracle_inline_datum.price_data.get_timestamp()

    async def get_oracle_expiration(self) -> int:
        """Get the oracle's feed exchange rate"""
        oracle_feed_utxo = await self.get_oracle_utxo()
        oracle_inline_datum: GenericData = GenericData.from_cbor(
            oracle_feed_utxo.output.datum.cbor
        )
        return oracle_inline_datum.price_data.get_expiry()

    async def get_oracle_utxo(self) -> pyc.UTxO:
        """Retrieve the oracle's feed UTXO using the NFT identifier."""
        oracle_utxos = await self.chain_query.get_utxos(str(self.oracle_addr))
        oracle_utxo_nft = next(
            utxo
            for utxo in oracle_utxos
            if utxo.output.amount.multi_asset == self.oracle_nft
        )
        return oracle_utxo_nft

    async def get_swap_utxo(self) -> pyc.UTxO:
        """Retrieve the UTxO for the swap using the NFT identifier"""
        swap_utxos = await self.chain_query.get_utxos(str(self.swap_addr))
        try:
            swap_utxo_nft = next(
                x
                for x in swap_utxos
                if x.output.amount.multi_asset >= self.swap.swap_nft
            )
            return swap_utxo_nft
        except StopIteration:
            raise ValueError("No matching UTxO found for the given NFT identifier")

    async def decrease_asset_swap(self, selling_amount: int) -> pyc.MultiAsset:
        """The updated swap asset to be decreased at the address"""
        ((policy_id, assets),) = self.swap.coinA.to_shallow_primitive().items()
        ((asset, _),) = assets.to_shallow_primitive().items()

        swap_utxo = await self.get_swap_utxo()
        m_assets = swap_utxo.output.amount.multi_asset.to_shallow_primitive()

        new_multi_asset_dict = pyc.MultiAsset()
        multi_asset_assets_names = pyc.Asset()
        for swap_policy_id, assets in m_assets.items():
            if swap_policy_id == policy_id:
                for asset_name, amount in assets.items():
                    if asset_name == asset:
                        multi_asset_assets_names[asset_name] = amount - selling_amount
                    else:
                        multi_asset_assets_names[asset_name] = amount
            else:
                new_multi_asset_dict[swap_policy_id] = assets
        new_multi_asset_dict[policy_id] = multi_asset_assets_names
        return new_multi_asset_dict

    async def decrease_asset_swap_amount(self, selling_amount: int) -> int:
        """The updated swap asset amount to be decreased at the address"""
        ((policy_id, assets),) = self.swap.coinA.to_shallow_primitive().items()
        ((asset, _),) = assets.to_shallow_primitive().items()

        swap_utxo = await self.get_swap_utxo()
        m_assets = swap_utxo.output.amount.multi_asset.to_shallow_primitive()

        amountA = 0
        for swap_policy_id, assets in m_assets.items():
            if swap_policy_id == policy_id:
                for asset_name, amount in assets.items():
                    if asset_name == asset:
                        amountA = amount - selling_amount
        return amountA

    async def add_asset_swap(self, buying_amount: int):
        """The updated swap asset to be added at the address"""
        ((coin_a_policy_id, assets),) = self.swap.coinA.to_shallow_primitive().items()
        ((coin_a_asset_name, _),) = assets.to_shallow_primitive().items()

        swap_utxo = await self.get_swap_utxo()
        has_coin_a_policy = swap_utxo.output.amount.multi_asset.get(
            coin_a_policy_id, None
        )

        if has_coin_a_policy:
            has_coin_a_asset_name = swap_utxo.output.amount.multi_asset[
                coin_a_policy_id
            ].get(coin_a_asset_name, None)
            if has_coin_a_asset_name:
                swap_utxo.output.amount.multi_asset[coin_a_policy_id][
                    coin_a_asset_name
                ] += buying_amount

            else:
                swap_utxo.output.amount.multi_asset[coin_a_policy_id][
                    coin_a_asset_name
                ] = buying_amount

        else:
            new_asset = pyc.Asset({coin_a_asset_name: buying_amount})
            swap_utxo.output.amount.multi_asset[coin_a_policy_id] = new_asset

        total_amount = swap_utxo.output.amount.multi_asset[coin_a_policy_id][
            coin_a_asset_name
        ]
        return swap_utxo.output.amount.multi_asset, total_amount

    async def add_asset_swap_amount(self, buying_amount: int) -> int:
        """The updated swap asset amount to be added at the address"""
        ((policy_id, assets),) = self.swap.coinA.to_shallow_primitive().items()
        ((asset, _),) = assets.to_shallow_primitive().items()

        swap_utxo = await self.get_swap_utxo()
        m_assets = swap_utxo.output.amount.multi_asset.to_shallow_primitive()

        amountA = 0
        for swap_policy_id, assets in m_assets.items():
            if swap_policy_id == policy_id:
                for asset_name, amount in assets.items():
                    if asset_name == asset:
                        amountA = amount + buying_amount
        return amountA

    async def take_multi_asset_user(self, buying_amount: int) -> pyc.MultiAsset:
        """The updated user asset to be added to it's wallet"""
        ((policy_id, assets),) = self.swap.coinA.to_shallow_primitive().items()
        ((asset, _),) = assets.to_shallow_primitive().items()

        swap_utxo = await self.get_swap_utxo()
        m_assets = swap_utxo.output.amount.multi_asset.to_shallow_primitive()

        new_multi_asset_dict = pyc.MultiAsset()
        multi_asset_assets_names = pyc.Asset()
        for swap_policy_id, assets in m_assets.items():
            if swap_policy_id == policy_id:
                for asset_name, _ in assets.items():
                    if asset_name == asset:
                        multi_asset_assets_names[asset_name] = buying_amount
        new_multi_asset_dict[policy_id] = multi_asset_assets_names
        return new_multi_asset_dict

    def available_user_pure_tlovelace(self, user_address: pyc.Address) -> int:
        """Get the available user's pure lovelace amount"""
        amount = 0
        for utxo in self.chain_query.utxos(str(user_address)):
            if not utxo.output.amount.multi_asset:
                amount += utxo.output.amount.coin
        return amount

    async def available_user_tlovelace(self, user_address: pyc.Address) -> int:
        """Get the available user's  lovelace amount"""
        amount = 0
        utxos = await self.chain_query.get_utxos(str(user_address))
        for utxo in utxos:
            amount += utxo.output.amount.coin
        return amount

    async def available_user_tusdt(self, user_address: pyc.Address) -> int:
        amount_asset = 0
        ((policy_id, assets),) = self.swap.coinA.to_shallow_primitive().items()
        ((asset, _),) = assets.to_shallow_primitive().items()
        utxos = await self.chain_query.get_utxos(str(user_address))
        for utxo in utxos:
            m_assets = utxo.output.amount.multi_asset.to_shallow_primitive()
            for user_policy_id, assets in m_assets.items():
                if user_policy_id == policy_id:
                    for asset_name, amount in assets.items():
                        if asset_name == asset:
                            amount_asset += amount
        return amount_asset
