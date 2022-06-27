from scripts.helpful_scripts import (
    encode_function_data,
    get_account,
    deploy_box_and_proxy,
    upgrade,
)
from brownie import (
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    exceptions,
)
import pytest


def test_proxy_upgrades():
    account = get_account()
    proxy_box = deploy_box_and_proxy()
    # now check data in Box contract
    assert proxy_box[2].retrieve() == 0
    # store data in it
    tx = proxy_box[2].store(2, {"from": account})
    tx.wait(1)
    assert proxy_box[2].retrieve() == 2

    proxy_box2 = Contract.from_abi("BoxV2", proxy_box[1].address, BoxV2.abi)
    # now we check to run the increment function of the BoxV2 but havent upgraded
    # our proxy so we expect get an vm error
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box2.increment({"from": account})

    # lets upgrade our contract
    box_v2 = BoxV2.deploy({"from": account})

    upgrade_transaction = upgrade(
        account,
        proxy_box[1],  # transparent_upgradeable_proxy
        box_v2.address,
        proxy_admin_contract=proxy_box[0],  # proxy admin
    )
    upgrade_transaction.wait(1)
    print("Proxy upgraded")

    tx = proxy_box2.increment({"from": account})
    tx.wait(1)
    assert (
        proxy_box2.retrieve() == 3
    )  # we stored at first in Box.sol the value 2, updated our contract and now used the increment fct so we expect now 3 in it


# def GetAttributeError():

#     proxy_box = deploy_box_and_proxy()
#     with proxy_box.assertRaises(Exception):
#         proxy_box.increment()
