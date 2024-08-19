import json
import os

from web3 import Web3
from web3.contract import Contract
from web3.types import TxReceipt

from .config import CONFIG


class UniswapV3Factory:

    def __init__(self, web3: Web3):
        """
        Initializes a new instance of the ``UniswapV3Factory`` class.

        :param web3: A ``Web3`` instance connected to a blockchain node.
        :type web3: ``Web3``
        """
        if str(web3.eth.chain_id) not in CONFIG.keys():
            raise ValueError(f"Unsupported chain (chain ID = {web3.eth.chain_id})")
        self.web3: Web3 = web3
        with open(
            os.path.join(os.path.dirname(__file__), "abi", "UniswapV3Factory.json"), "r"
        ) as file:
            self.contract: Contract = self.web3.eth.contract(
                address=CONFIG[str(self.web3.eth.chain_id)]["factory"],
                abi=json.load(file),
            )

    def get_pool(self, token_a: str, token_b: str, fee: int) -> str:
        """
        Returns the address of the pool for ``token_a`` and ``token_b`` with a given fee
        if it has been created, else returns the null address

        :param token_a: The address of the first token.
        :type token_a: str
        :param token_b: The address of the second token.
        :type token_b: str
        :param fee: The pool's fee denominated in hundredths of a basis point (i.e.,
            1e-6). Must be one of the following: 500, 3000, 10000.

        :return: The address of the pair.
        :rtype: str
        """
        return self.contract.functions.getPool(
            self.web3.to_checksum_address(token_a),
            self.web3.to_checksum_address(token_b),
            fee,
        ).call()
