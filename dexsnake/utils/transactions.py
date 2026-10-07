from typing import Optional

from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.types import TxReceipt


def _send_transaction(
    web3: Web3,
    function: ContractFunction,
    account: str,
    private_key: str,
    gas: Optional[int],
    gas_price: Optional[int],
) -> TxReceipt:
    account_checksum = web3.to_checksum_address(account)
    if gas_price is None:
        gas_price = web3.eth.gas_price
    tx_params = {
        "from": account_checksum,
        "nonce": web3.eth.get_transaction_count(account_checksum, "pending"),
        "gasPrice": gas_price,
    }
    if gas is not None:
        tx_params["gas"] = gas
    tx = function.build_transaction(tx_params)
    signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt["status"] == 0:
        raise RuntimeError(f"Transaction {Web3.to_hex(tx_hash)} failed")
    return receipt
