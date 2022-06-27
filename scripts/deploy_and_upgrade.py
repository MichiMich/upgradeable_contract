import py
from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    BoxV2,
    BoxV3,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
)


def main():
    account = get_account()
    print(f"deploying to {network.show_active()}")
    box = Box.deploy(
        {"from": account},
    )
    print(f"value from deployed box {box.retrieve()}")

    proxy_admin = ProxyAdmin.deploy({"from": account})

    # initializer = box.store, 1
    box_encoded_initializer_function = (
        encode_function_data()
    )  # empty means dont use an initializer
    # proxies sometimes have a hard time figuring out gas limits, so we add one
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    # without proxy, call a function of contract: box.retrieve() or box.store(1)
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    StoreCalledByProxy = proxy_box.store(1, {"from": account})
    print(
        f"value from proxy of box {proxy_box.retrieve()}"
    )  # delegate call with proxy to box.retrieve()
    StoreCalledByProxy.wait(1)  # for brownie to not end with an error
    # proxy_box.increment({"from": account}) #this call fails, because our box has no function with increment, the new boxv2 would have

    # upgrade our proxy
    box_v2 = BoxV2.deploy({"from": account})
    upgrade_transaction = upgrade(
        account,
        proxy,
        box_v2.address,
        proxy_admin_contract=proxy_admin,
    )
    upgrade_transaction.wait(1)
    print("Proxy upgraded")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(f"NewValueAfterIncrementFromBoxV2 {proxy_box.retrieve()}")

    box_v3 = BoxV3.deploy({"from": account})
    upgrade_transaction = upgrade(
        account,
        proxy,
        box_v3.address,
        proxy_admin_contract=proxy_admin,
    )
    upgrade_transaction.wait(1)
    print("Proxy upgraded again")
    proxy_box = Contract.from_abi("BoxV3", proxy.address, BoxV3.abi)
    tx = proxy_box.incrementBy2({"from": account})
    print(f"NewValueAfterIncrementFromBoxV2 {proxy_box.retrieve()}")
    tx.wait(1)
