import json
import os
from typing import Any, List, Optional

from web3 import Web3
from web3.contract import Contract
from web3.types import TxReceipt

from .config import CONFIG


class UniswapV2Factory:

    def __init__(self, web3: Web3):
        """
        Initializes the factory object.

        :param web3: An initialized Web3 object.
        :type web3: Web3
        """
        if str(web3.eth.chain_id) not in CONFIG.keys():
            raise ValueError(f"Unsupported chain (chain ID = {web3.eth.chain_id})")
        self.web3 = web3
        with open(
            os.path.join(os.path.dirname(__file__), "abi", "UniswapV2Factory.json"), "r"
        ) as file:
            self.contract: Contract = self.web3.eth.contract(
                address=CONFIG[str(self.web3.eth.chain_id)]["factory"],
                abi=json.load(file)["abi"],
            )

    def get_pair(self, token_a: str, token_b: str) -> str:
        """
        Returns the address of the pair for ``token_a`` and ``token_b`` if it has been
        created, else returns the null address

        :param token_a: The address of the first token.
        :type token_a: str
        :param token_b: The address of the second token.
        :type token_b: str
        :return: The address of the pair.
        :rtype: str
        """
        return self.contract.functions.getPair(
            self.web3.to_checksum_address(token_a),
            self.web3.to_checksum_address(token_b),
        ).call()
