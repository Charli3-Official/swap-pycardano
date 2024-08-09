import os

from pycardano import (
    Address,
    ExtendedSigningKey,
    HDWallet,
    Network,
    PaymentSigningKey,
    PaymentVerificationKey,
)

# MNEMONIC_24 = "net subject gown ask suspect mango hammer picnic bridge interest world neglect salon cycle crater fat grocery sausage harvest poverty hurt zone arrow slow"

# USER
MNEMONIC_24 = "atom during negative faculty enable brand limb jaguar stumble again exchange bleak over chimney tide slice parent possible answer relax rebuild civil puzzle catalog"


def user_address() -> Address:
    hdwallet = HDWallet.from_mnemonic(MNEMONIC_24)
    hdwallet_spend = hdwallet.derive_from_path("m/1852'/1815'/0'/0/0")
    spend_public_key = hdwallet_spend.public_key
    spend_vk = PaymentVerificationKey.from_primitive(spend_public_key)

    hdwallet_stake = hdwallet.derive_from_path("m/1852'/1815'/0'/2/0")
    stake_public_key = hdwallet_stake.public_key
    stake_vk = PaymentVerificationKey.from_primitive(stake_public_key)

    str_address = Address(
        spend_vk.hash(), stake_vk.hash(), network=Network.TESTNET
    ).encode()
    return Address.from_primitive(str_address)


def user_credentials() -> Address:
    hdwallet = HDWallet.from_mnemonic(MNEMONIC_24)
    hdwallet_spend = hdwallet.derive_from_path("m/1852'/1815'/0'/0/0")
    spend_public_key = hdwallet_spend.public_key
    spend_vk = PaymentVerificationKey.from_primitive(spend_public_key)

    hdwallet_stake = hdwallet.derive_from_path("m/1852'/1815'/0'/2/0")
    stake_public_key = hdwallet_stake.public_key
    stake_vk = PaymentVerificationKey.from_primitive(stake_public_key)

    str_address = Address(
        spend_vk.hash(), stake_vk.hash(), network=Network.TESTNET
    ).encode()
    return spend_vk, stake_vk


def user_esk() -> PaymentSigningKey:
    hdwallet = HDWallet.from_mnemonic(MNEMONIC_24)
    hdwallet_spend = hdwallet.derive_from_path("m/1852'/1815'/0'/0/0")

    extended_signing_key = ExtendedSigningKey.from_hdwallet(hdwallet_spend)
    return extended_signing_key


user_address()
user_esk()
