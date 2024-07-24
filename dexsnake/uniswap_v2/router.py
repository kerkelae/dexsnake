import json
import os
import time
from typing import Any, List, Optional, Tuple

from web3 import Web3
from web3.contract import Contract
from web3.types import FilterParams, TxReceipt

from .config import CONFIG


class UniswapV2Router:

    def __init__(self, web3: Web3):
        """
        Initializes the router object.

        :param web3: An initialized Web3 object.
        :type web3: Web3
        """
        if str(web3.eth.chain_id) not in CONFIG.keys():
            raise ValueError(f"Unsupported chain (chain ID = {web3.eth.chain_id})")
        self.web3 = web3
        with open(
            os.path.join(os.path.dirname(__file__), "abi", "UniswapV2Router02.json"),
            "r",
        ) as file:
            self.contract: Contract = self.web3.eth.contract(
                address=CONFIG[str(self.web3.eth.chain_id)]["router_02"],
                abi=json.load(file)["abi"],
            )

    def swap_exact_tokens_for_tokens(
        self,
        amount_in: int,
        amount_out_min: int,
        path: List[str],
        to: str,
        account: str,
        private_key: str,
        deadline: Optional[int] = None,
        gas: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> TxReceipt:
        """
        Swaps an exact amount of input tokens for as many output tokens as possible,
        along the route determined by ``path``.

        :param amount_in: The amount of input tokens to send.
        :type amount_in: int
        :param amount_out_min: The minimum amount of output tokens that must be received
            for the transaction not to revert.
        :type amount_out_min: int
        :param path: A list of token addresses. The length of ``path`` must be >= 2 and
            pools for each consecutive pair of addresses must exist and have liquidity.
        :type path: List[str]
        :param to: The recipient of the output tokens.
        :type to: str
        :param account: The account address from which the transaction will be sent.
        :type account: str
        :param private_key: The private key of the account.
        :type private_key: str
        :param deadline: The Unix timestamp after which the transaction will revert. If
            not provided, it will be set to five minutes from the current time.
        :type deadline: int, optional
        :param gas: The gas limit for the transaction. If not provided, it will be
            estimated automatically.
        :type gas: int, optional
        :param gas_price: The gas price for the transaction in wei. If not provided, the
            current network gas price will be used.
        :type gas_price: int, optional

        :return: The transaction receipt of the swap operation.
        :rtype: TxReceipt
        """
        if gas_price is None:
            gas_price = self.web3.eth.gas_price
        if deadline is None:
            deadline = int(time.time() + 300)
        tx = self.contract.functions.swapExactTokensForTokens(
            amount_in,
            amount_out_min,
            [self.web3.to_checksum_address(address) for address in path],
            to,
            deadline,
        ).buildTransaction(
            {
                "from": account,
                "nonce": self.web3.eth.get_transaction_count(account),
                "gasPrice": gas_price,
            }
        )
        if gas is None:
            gas = self.web3.eth.estimate_gas(tx)
        tx["gas"] = gas
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def swap_tokens_for_exact_tokens(
        self,
        amount_out: int,
        amount_in_max: int,
        path: List[str],
        to: str,
        account: str,
        private_key: str,
        deadline: Optional[int] = None,
        gas: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> TxReceipt:
        """
        Swaps an exact amount of input tokens for as many output tokens as possible,
        along the route determined by ``path``.

        :param amount_out: The amount of input tokens to receive.
        :type amount_out: int
        :param amount_out_max: The maximum amount of input tokens that must be received
            for the transaction not to revert.
        :type amount_out_max: int
        :param path: A list of token addresses. The length of ``path`` must be >= 2 and
            pools for each consecutive pair of addresses must exist and have liquidity.
        :type path: List[str]
        :param to: The recipient of the output tokens.
        :type to: str
        :param account: The account address from which the transaction will be sent.
        :type account: str
        :param private_key: The private key of the account.
        :type private_key: str
        :param deadline: The Unix timestamp after which the transaction will revert. If
            not provided, it will be set to five minutes from the current time.
        :type deadline: int, optional
        :param gas: The gas limit for the transaction. If not provided, it will be
            estimated automatically.
        :type gas: int, optional
        :param gas_price: The gas price for the transaction in wei. If not provided, the
            current network gas price will be used.
        :type gas_price: int, optional

        :return: The transaction receipt of the swap operation.
        :rtype: TxReceipt
        """
        if gas_price is None:
            gas_price = self.web3.eth.gas_price
        if deadline is None:
            deadline = int(time.time() + 300)
        tx = self.contract.functions.swapTokensForExactTokens(
            amount_out,
            amount_in_max,
            [self.web3.to_checksum_address(address) for address in path],
            to,
            deadline,
        ).buildTransaction(
            {
                "from": account,
                "nonce": self.web3.eth.get_transaction_count(account),
                "gasPrice": gas_price,
            }
        )
        if gas is None:
            gas = self.web3.eth.estimate_gas(tx)
        tx["gas"] = gas
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)
