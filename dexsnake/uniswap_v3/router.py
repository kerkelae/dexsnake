from decimal import Decimal
import json
import os
import time
from typing import Optional

from web3 import Web3
from web3.contract import Contract
from web3.types import TxReceipt

from .config import CONFIG
from ..utils.erc20_token import ERC20Token


class UniswapV3Router:

    def __init__(self, web3: Web3):
        """
        Initializes a new instance of the ``UniswapV3Router`` class.

        :param web3: A ``Web3`` instance connected to a blockchain node.
        :type web3: ``Web3``
        """
        if str(web3.eth.chain_id) not in CONFIG.keys():
            raise ValueError(f"Unsupported chain (chain ID = {web3.eth.chain_id})")
        self.web3: Web3 = web3
        with open(
            os.path.join(
                os.path.dirname(__file__), "abi", "UniswapV3SwapRouter02.json"
            ),
            "r",
        ) as file:
            self.contract: Contract = self.web3.eth.contract(
                address=CONFIG[str(self.web3.eth.chain_id)]["swap_router_02"],
                abi=json.load(file),
            )

    def exact_input_single(
        self,
        amount_in: Decimal,
        amount_out_min: Decimal,
        token_in: str,
        token_out: str,
        fee: int,
        recipient: str,
        account: str,
        private_key: str,
        deadline: Optional[int] = None,
        gas: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> TxReceipt:
        """
        Swaps an exact amount of input tokens for as many output tokens as possible, in
        a single Uniswap V3 pool defined by the token pair and fee.

        :param amount_in: The amount of input tokens to send.
        :type amount_in: ``Decimal``
        :param amount_out_min: The minimum amount of output tokens that must be received
            for the transaction not to revert.
        :type amount_out_min: ``Decimal``
        :param token_in: The address of the input token.
        :type token_in: str
        :param token_out: The address of the output token.
        :type token_out: str
        :param fee: The pool's fee denominated in hundredths of a basis point (i.e.,
            1e-6). Must be one of the following: 500, 3000, 10000.
        :type fee: int
        :param recipient: The recipient of the output tokens.
        :type recipient: str
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
        token_in_decimals = ERC20Token(
            self.web3, self.web3.to_checksum_address(token_in)
        ).decimals
        token_out_decimals = ERC20Token(
            self.web3, self.web3.to_checksum_address(token_out)
        ).decimals
        params = {
            "tokenIn": self.web3.to_checksum_address(token_in),
            "tokenOut": self.web3.to_checksum_address(token_out),
            "fee": fee,
            "recipient": self.web3.to_checksum_address(recipient),
            "deadline": deadline,
            "amountIn": int(Decimal(amount_in) * Decimal(10**token_in_decimals)),
            "amountOutMinimum": int(
                Decimal(amount_out_min) * Decimal(10**token_out_decimals)
            ),
            "sqrtPriceLimitX96": 0,
        }
        tx = self.contract.functions.exactInputSingle(params).build_transaction(
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

    def exact_output_single(
        self,
        amount_out: Decimal,
        amount_in_max: Decimal,
        token_in: str,
        token_out: str,
        fee: int,
        recipient: str,
        account: str,
        private_key: str,
        deadline: Optional[int] = None,
        gas: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> TxReceipt:
        """
        Swaps as few input tokens as possible for an exact amount of output tokens, in
        a single Uniswap V3 pool defined by the token pair and fee.

        :param amount_out: The amount of output tokens to receive.
        :type amount_out: ``Decimal``
        :param amount_in_max: The maximum amount of input tokens that can be sent.
        :type amount_in_max: ``Decimal``
        :param token_in: The address of the input token.
        :type token_in: str
        :param token_out: The address of the output token.
        :type token_out: str
        :param fee: The pool's fee denominated in hundredths of a basis point (i.e.,
            1e-6). Must be one of the following: 500, 3000, 10000.
        :type fee: int
        :param recipient: The recipient of the output tokens.
        :type recipient: str
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
        token_in_decimals = ERC20Token(
            self.web3, self.web3.to_checksum_address(path[0])
        ).decimals
        token_out_decimals = ERC20Token(
            self.web3, self.web3.to_checksum_address(path[-1])
        ).decimals
        params = {
            "tokenIn": self.web3.to_checksum_address(token_in),
            "tokenOut": self.web3.to_checksum_address(token_out),
            "fee": fee,
            "recipient": self.web3.to_checksum_address(recipient),
            "deadline": deadline,
            "amountOut": int(Decimal(amount_out) * Decimal(10**token_out_decimals)),
            "amountInMaximum": int(
                Decimal(amount_in_max) * Decimal(10**token_in_decimals)
            ),
            "sqrtPriceLimitX96": 0,
        }
        tx = self.contract.functions.exactOutputSingle(params).build_transaction(
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
