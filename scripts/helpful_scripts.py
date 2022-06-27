from brownie import (
    network,
    accounts,
    config,
    interface,
    Contract,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
)
import os

import eth_utils

OPENSEA_FORMAT = "https://testnets.opensea.io/assets/{}/{}"
NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]

# contract_to_mock = {
#     "link_token": LinkToken,
#     "eth_usd_price_feed": MockV3Aggregator,
#     "vrf_coordinator": VRFCoordinatorMock,
#     "oracle": MockOracle,
# }


def deploy_box_and_proxy():  # returns proxy_admin, transparent_upgradeable_proxy, proxy_box
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    box_encoded_initializer_function = encode_function_data()
    transparent_upgradeable_proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    proxy_box = Contract.from_abi("Box", transparent_upgradeable_proxy.address, Box.abi)
    return proxy_admin, transparent_upgradeable_proxy, proxy_box


# def deploy_transparentUpgradeableProxy():
#     proxy = TransparentUpgradeableProxy.deploy(
#         box.address,
#         proxy_admin.address,
#         box_encoded_initializer_function,
#         {"from": account, "gas_limit": 1000000},
#     )


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None


# initializer=box.store, 1, 2, 3, 4, 5
def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.
        args (Any, optional):
        The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if (
        len(args) == 0 or not initializer
    ):  # hack so brownie dont runs into an issue here with the encode_input()
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)  # build in function from brownie


def upgrade(
    account,
    proxy,
    new_implemenation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args
):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_implemenation_address,
                encode_function_call,
                {"from": account},
            )
        else:
            # no initializer->no encode of tx call
            transaction = proxy_admin_contract.upgrade(
                proxy.address,
                new_implemenation_address,
                {"from": account},
            )
    else:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                new_implemenation_address, encode_function_call, {"from": account}
            )
        else:
            transaction = proxy.upgradeTo(new_implemenation_address, {"from": account})
    return transaction
