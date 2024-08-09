"""offchain code containing mint class"""

from dataclasses import dataclass

from charli3_offchain_core.chain_query import ChainQuery
from pycardano import (
    Address,
    AlonzoMetadata,
    AuxiliaryData,
    Metadata,
    MultiAsset,
    PaymentSigningKey,
    PlutusData,
    PlutusV2Script,
    Redeemer,
    TransactionBuilder,
    TransactionOutput,
    Unit,
    Value,
    plutus_script_hash,
)


@dataclass
class MintToken(PlutusData):
    CONSTR_ID = 0


class Mint:
    def __init__(
        self,
        chain_query: ChainQuery,
        signing_key: PaymentSigningKey,
        user_address: Address,
        swap_address: Address,
        plutus_v2_mint_script: PlutusV2Script,
    ) -> None:
        self.chain_query = chain_query
        self.signing_key = signing_key
        self.user_address = user_address
        self.swap_address = swap_address
        self.minting_script_plutus_v2 = plutus_v2_mint_script

    async def mint_nft_with_script(self):
        """mint tokens with plutus v2 script"""
        policy_id = plutus_script_hash(self.minting_script_plutus_v2)
        asset_name = "SWAP"
        nft_swap = MultiAsset.from_primitive(
            {
                policy_id.payload: {
                    bytes(asset_name, "utf-8"): 1,
                }
            }
        )

        metadata = {
            0: {
                policy_id.payload.hex(): {
                    "Swap": {
                        "description": "This is a test token",
                        "name": asset_name,
                    }
                }
            }
        }

        print(
            f"Swap's NFT information:\nCurrency Symbol (Policy ID): {policy_id.payload.hex()}\nToken Name: {asset_name}"
        )
        # Place metadata in AuxiliaryData, the format acceptable by a transaction.
        auxiliary_data = AuxiliaryData(AlonzoMetadata(metadata=Metadata(metadata)))

        # Create a transaction builder
        builder = TransactionBuilder(self.chain_query.context)

        # Add our own address as the input address
        builder.add_input_address(self.user_address)

        # Add minting script with an empty datum and a minting redeemer
        builder.add_minting_script(
            self.minting_script_plutus_v2,
            redeemer=Redeemer(MintToken()),
        )

        # Set nft we want to mint
        builder.mint = nft_swap

        # Set transaction metadata
        builder.auxiliary_data = auxiliary_data

        # Add the minimum lovelace amount to the user value
        value_swap_utxo = Value(coin=2000000, multi_asset=nft_swap)
        # Send the NFT to our own address
        swap_nft_output = TransactionOutput(
            address=self.swap_address, amount=value_swap_utxo, datum=Unit()
        )

        builder.add_output(swap_nft_output)

        await self.chain_query.submit_tx_builder(
            builder, self.signing_key, self.user_address
        )
