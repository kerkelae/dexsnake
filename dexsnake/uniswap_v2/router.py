import json
import os
import time
from decimal import Decimal
from typing import List, Optional

from web3 import Web3
from web3.contract import Contract
from web3.types import TxReceipt

from ..utils.amounts import _to_base_units
from ..utils.erc20_token import ERC20Token
from ..utils.transactions import _send_transaction
from .config import CONFIG


class UniswapV2Router:
    def __init__(self, web3: Web3):
        """
        Initializes a new instance of the ``UniswapV2Router`` class.

        :param web3: A ``Web3`` instance connected to a blockchain node.
        :type web3: ``Web3``
        """
        if str(web3.eth.chain_id) not in CONFIG.keys():
            raise ValueError(f"Unsupported chain (chain ID = {web3.eth.chain_id})")
        self.web3: Web3 = web3
        with open(
            os.path.join(os.path.dirname(__file__), "abi", "UniswapV2Router02.json"),
            "r",
        ) as file:
            self.contract: Contract = self.web3.eth.contract(
                address=CONFIG[str(self.web3.eth.chain_id)]["router_02"],
                abi=json.load(file),
            )

    def swap_exact_tokens_for_tokens(
        self,
        amount_in: Decimal,
        amount_out_min: Decimal,
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
        :type amount_in: ``Decimal``
        :param amount_out_min: The minimum amount of output tokens that must be received
            for the transaction not to revert.
        :type amount_out_min: ``Decimal``
        :param path: A list of token addresses. The length of ``path`` must be >= 2 and
            Uniswap V2 pairs for each consecutive pair of addresses must exist and have
            liquidity.
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
        :param gas_price: The gas price for the transaction in wei (i.e., 1e-18 ETH). If
            not provided, the current network gas price will be used.
        :type gas_price: int, optional

        :return: The transaction receipt.
        :rtype: TxReceipt
        """
        if deadline is None:
            deadline = int(time.time() + 300)
        path_checksum = [self.web3.to_checksum_address(address) for address in path]
        token_in_decimals = ERC20Token(self.web3, path_checksum[0]).decimals
        token_out_decimals = ERC20Token(self.web3, path_checksum[-1]).decimals
        function = self.contract.functions.swapExactTokensForTokens(
            _to_base_units(amount_in, token_in_decimals),
            _to_base_units(amount_out_min, token_out_decimals),
            path_checksum,
            self.web3.to_checksum_address(to),
            deadline,
        )
        return _send_transaction(self.web3, function, account, private_key, gas, gas_price)

    def swap_tokens_for_exact_tokens(
        self,
        amount_out: Decimal,
        amount_in_max: Decimal,
        path: List[str],
        to: str,
        account: str,
        private_key: str,
        deadline: Optional[int] = None,
        gas: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> TxReceipt:
        """
        Swaps as few input tokens as possible for an exact amount of output tokens,
        along the route determined by ``path``.

        :param amount_out: The amount of output tokens to receive.
        :type amount_out: ``Decimal``
        :param amount_in_max: The maximum amount of input tokens that can be sent
            for the transaction not to revert.
        :type amount_in_max: ``Decimal``
        :param path: A list of token addresses. The length of ``path`` must be >= 2 and
            Uniswap V2 pairs for each consecutive pair of addresses must exist and have
            liquidity.
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
        :param gas_price: The gas price for the transaction in wei (i.e., 1e-18 ETH). If
            not provided, the current network gas price will be used.
        :type gas_price: int, optional

        :return: The transaction receipt.
        :rtype: TxReceipt
        """
        if deadline is None:
            deadline = int(time.time() + 300)
        path_checksum = [self.web3.to_checksum_address(address) for address in path]
        token_in_decimals = ERC20Token(self.web3, path_checksum[0]).decimals
        token_out_decimals = ERC20Token(self.web3, path_checksum[-1]).decimals
        function = self.contract.functions.swapTokensForExactTokens(
            _to_base_units(amount_out, token_out_decimals),
            _to_base_units(amount_in_max, token_in_decimals),
            path_checksum,
            self.web3.to_checksum_address(to),
            deadline,
        )
        return _send_transaction(self.web3, function, account, private_key, gas, gas_price)
