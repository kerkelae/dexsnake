from typing import Optional

from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.types import TxReceipt


def _send_transaction(
    web3: Web3,
    function: ContractFunction,
    private_key: str,
    gas: Optional[int],
    gas_price: Optional[int],
) -> TxReceipt:
    account = web3.eth.account.from_key(private_key)
    if gas_price is None:
        gas_price = web3.eth.gas_price
    tx_params = {
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address, "pending"),
        "gasPrice": gas_price,
    }
    if gas is not None:
        tx_params["gas"] = gas
    tx = function.build_transaction(tx_params)
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt["status"] == 0:
        raise RuntimeError(f"Transaction {Web3.to_hex(tx_hash)} failed")
    return receipt
