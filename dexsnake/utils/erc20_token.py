from decimal import Decimal
import json
import os
from typing import Optional

from web3 import Web3
from web3.contract import Contract
from web3.types import TxReceipt


class ERC20Token:

    def __init__(self, web3: Web3, address: str):
        """
        Initializes a new instance of the ``ERC20Token`` class.

        For details about the ERC20 standard, see https://eips.ethereum.org/EIPS/eip-20.

        :param web3: A ``Web3`` instance connected to a blockchain node.
        :type web3: ``Web3``
        :param address: The address of the ERC20 token contract.
        :type address: str
        """
        self.web3: Web3 = web3
        self.address: str = address
        abi_path = os.path.join(os.path.dirname(__file__), "abi", "ERC20Token.json")
        with open(abi_path, "r") as file:
            self.contract: Contract = self.web3.eth.contract(
                address=self.address, abi=json.load(file)
            )
        self._name: Optional[str] = None
        self._symbol: Optional[str] = None
        self._decimals: Optional[int] = None

    def allowance(self, owner: str, spender: str) -> Decimal:
        """
        Returns the amount which ``spender`` is allowed to withdraw from ``owner``.

        :param owner: The address of the token owner.
        :type owner: str
        :param spender: The address of the spender.
        :type spender: str

        :return: The remaining allowance of tokens.
        :rtype: ``Decimal``
        """
        return Decimal(self.contract.functions.allowance(owner, spender).call()) / (
            Decimal(10**self.decimals)
        )

    def approve(
        self,
        spender: str,
        value: Decimal,
        account: str,
        private_key: str,
        gas: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> TxReceipt:
        """
        Approves the specified address to spend the specified amount of tokens on behalf
        of the caller.

        :param spender: The address to approve.
        :type spender: str
        :param value: The amount of tokens to approve.
        :type value: ``Decimal``
        :param account: The account address from which the transaction will be sent.
        :type account: str
        :param private_key: The private key of the account.
        :type private_key: str
        :param gas: The gas limit for the transaction. If not provided, it will be
            estimated automatically.
        :type gas: int, optional
        :param gas_price: The gas price for the transaction in wei. If not provided, the
            current network gas price will be used.
        :type gas_price: int, optional

        :return: The transaction receipt.
        :rtype: TxReceipt
        """
        if gas_price is None:
            gas_price = self.web3.eth.gas_price
        tx = self.contract.functions.approve(
            spender,
            int(value * Decimal(10**self.decimals)),
        ).build_transaction(
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

    def balance_of(self, account: str) -> Decimal:
        """
        Returns the balance of the specified account.

        :param account: The address of the account.
        :type account: str

        :return: The balance of the account.
        :rtype: ``Decimal``
        """
        return Decimal(self.contract.functions.balanceOf(account).call()) / Decimal(
            10**self.decimals
        )

    @property
    def decimals(self) -> int:
        """
        Returns the number of decimals the token uses.

        :return: The number of decimals.
        """
        if self._decimals is None:
            self._decimals = self.contract.functions.decimals().call()
        return self._decimals

    @property
    def name(self) -> str:
        """
        Returns the name of the token.

        :return: The token name.
        """
        if self._name is None:
            self._name = self.contract.functions.name().call()
        return self._name

    @property
    def symbol(self) -> str:
        """
        Returns the symbol of the token.

        :return: The token symbol.
        """
        if self._symbol is None:
            self._symbol = self.contract.functions.symbol().call()
        return self._symbol

    def total_supply(self) -> Decimal:
        """
        Returns the total supply of the token.

        :return: Total token supply.
        :rtype: ``Decimal``
        """
        return Decimal(self.contract.functions.totalSupply().call()) / Decimal(
            10**self.decimals
        )

    def transfer(
        self,
        to: str,
        value: Decimal,
        account: str,
        private_key: str,
        gas: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> TxReceipt:
        """
        Transfers tokens to the specified address.

        :param to: The address to transfer tokens to.
        :type to: str
        :param value: The amount of tokens to transfer.
        :type value: float
        :param account: The account address from which the transaction will be sent.
        :type account: str
        :param private_key: The private key of the account.
        :type private_key: str
        :param gas: The gas limit for the transaction. If not provided, it will be
            estimated automatically.
        :type gas: int, optional
        :param gas_price: The gas price for the transaction in wei. If not provided, the
            current network gas price will be used.
        :type gas_price: int, optional

        :return: The transaction receipt.
        :rtype: TxReceipt
        """
        if gas_price is None:
            gas_price = self.web3.eth.gas_price
        tx = self.contract.functions.transfer(
            to,
            int(value * Decimal(10**self.decimals)),
        ).build_transaction(
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
