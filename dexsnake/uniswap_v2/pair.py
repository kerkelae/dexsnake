import json
import math
import os
from typing import Optional, Tuple

from web3 import Web3
from web3.contract import Contract

from .config import CONFIG
from ..utils.erc20_token import ERC20Token


class UniswapV2Pair:

    def __init__(self, web3: Web3, address: str):
        """
        Initializes a new instance of the ``UniswapV2Pair`` class.

        :param web3: A ``Web3`` instance connected to a blockchain node.
        :type web3: ``Web3``
        :param address: The address of the pair contract.
        :type address: str
        """
        if str(web3.eth.chain_id) not in CONFIG.keys():
            raise ValueError(f"Unsupported chain (chain ID = {web3.eth.chain_id})")
        self.web3: Web3 = web3
        with open(
            os.path.join(os.path.dirname(__file__), "abi", "UniswapV2Pair.json"), "r"
        ) as file:
            self.contract: Contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(address),
                abi=json.load(file),
            )
        self._token_0: Optional[ERC20Token] = None
        self._token_1: Optional[ERC20Token] = None

    @property
    def token_0(self) -> ERC20Token:
        """
        Returns the ``ERC20Token`` instance representing the first token in the pair.

        :return: An ``ERC20Token`` instance representing the first token.
        :rtype: ``ERC20Token``
        """
        if self._token_0 is None:
            self._token_0 = ERC20Token(
                self.web3, self.contract.functions.token0().call()
            )
        return self._token_0

    @property
    def token_1(self) -> ERC20Token:
        """
        Returns the ``ERC20Token`` instance representing the second token in the pair.

        :return: An ``ERC20Token`` instance representing the second token.
        :rtype: ``ERC20Token``
        """
        if self._token_1 is None:
            self._token_1 = ERC20Token(
                self.web3, self.contract.functions.token1().call()
            )
        return self._token_1

    def get_reserves(self) -> Tuple[float, float]:
        """
        Returns the current reserves of ``token_0`` and ``token_1`` after taking into
        account the token decimals.

        :return: A tuple containing the pair's current reserves.
        :rtype: Tuple[float, float]
        """
        reserve_0, reserve_1, _ = (
            self.contract.functions.getReserves().call()
        )  # the third element is the timestamp when the reserves were last updated
        return (
            reserve_0 / 10**self.token_0.decimals,
            reserve_1 / 10**self.token_1.decimals,
        )

    def get_price(self) -> float:
        """
        Returns the current price of ``token_0`` denominated in ``token_1``.

        :return: The pair's current price.
        :rtype: float
        """
        reserve_0, reserve_1 = self.get_reserves()
        if reserve_0 == 0:
            return math.inf
        return reserve_1 / reserve_0
