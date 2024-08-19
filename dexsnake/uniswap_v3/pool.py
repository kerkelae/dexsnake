import json
import os
from typing import Tuple, Dict

from web3 import Web3
from web3.contract import Contract

from .config import CONFIG
from ..utils.erc20_token import ERC20Token


class UniswapV3Pool:

    def __init__(self, web3: Web3, address: str):
        """
        Initializes a new instance of the ``UniswapV3Pool`` class.

        :param web3: A ``Web3`` instance connected to a blockchain node.
        :type web3: ``Web3``
        :param address: The address of the pool contract.
        :type address: str
        """
        if str(web3.eth.chain_id) not in CONFIG.keys():
            raise ValueError(f"Unsupported chain (chain ID = {web3.eth.chain_id})")
        self.web3 = web3
        with open(
            os.path.join(os.path.dirname(__file__), "abi", "UniswapV3Pool.json"), "r"
        ) as file:
            self.contract: Contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(address),
                abi=json.load(file),
            )
        self._token_0: Optional[ERC20Token] = None
        self._token_1: Optional[ERC20Token] = None
        self._fee: Optional[int] = None

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

    @property
    def fee(self) -> int:
        """
        Returns the pool's fee denominated in hundredths of a basis point (i.e., 1e-6).

        :return: The fee tier of the pool.
        :rtype: int
        """
        if self._fee is None:
            self._fee = self.contract.functions.fee().call()
        return self._fee

    def get_price(self) -> float:
        """
        Returns the current price of ``token_0`` denominated in ``token_1`` in the pool.

        :return: The current price in the pool.
        :rtype: float
        """
        slot_0 = self.contract.functions.slot0().call()
        sqrt_price_x96 = slot_0[0]
        price = (sqrt_price_x96 / (2**96)) ** 2 * 10 ** (
            self.token_0.decimals - self.token_1.decimals
        )
        return price
