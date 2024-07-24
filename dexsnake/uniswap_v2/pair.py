import json
import os
from typing import List

from web3 import Web3
from web3.contract import Contract

from .config import CONFIG


class UniswapV2Pair:

    def __init__(self, web3: Web3, address: str):
        """
        Initializes the pair object.

        :param web3: An initialized Web3 object.
        :type web3: Web3
        :param address: The address of the Uniswap V2 pair contract.
        :type address: str
        """
        if str(web3.eth.chain_id) not in CONFIG.keys():
            raise ValueError(f"Unsupported chain (chain ID = {web3.eth.chain_id})")
        self.web3 = web3
        with open(
            os.path.join(os.path.dirname(__file__), "abi", "UniswapV2Pair.json"), "r"
        ) as file:
            self.contract: Contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(address),
                abi=json.load(file)["abi"],
            )
        self._token_0 = None
        self._token_1 = None

    @property
    def token_0(self) -> str:
        """
        Returns the address of the first token in the pair.

        :return: The address of the first token.
        :rtype: str
        """
        if self._token_0 is None:
            self._token_0 = self.contract.functions.token0().call()
        return self._token_0

    @property
    def token_1(self) -> str:
        """
        Returns the address of the second token in the pair.

        :return: The address of the second token.
        :rtype: str
        """
        if self._token_1 is None:
            self._token_1 = self.contract.functions.token1().call()
        return self._token_1

    def get_reserves(self) -> List[int]:
        """
        Returns the reserves of ``token_0`` and ``token_1``.

        :return: A list containing the reserves for ``token_0``, ``token_1``, and the
            block timestamp for last time the reserves were updated.
        :rtype: List[int]
        """
        return self.contract.functions.getReserves().call()
