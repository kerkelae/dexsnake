"""Opt-in transaction tests against a local Anvil mainnet fork.

Run with RUN_FORK_TESTS=1 pytest -m fork.
Anvil reads mainnet state, but every transaction is sent to localhost.
"""

import os
import shutil
import socket
import subprocess
import time
from decimal import Decimal

import pytest
from web3 import Web3

from dexsnake.uniswap_v2 import UniswapV2Router
from dexsnake.uniswap_v3 import UniswapV3Router
from dexsnake.utils.erc20_token import ERC20Token

pytestmark = pytest.mark.fork

FORK_BLOCK = 20_000_000
DEFAULT_RPC_URL = "https://ethereum.reth.rs/rpc"
WETH = Web3.to_checksum_address("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
USDC = Web3.to_checksum_address("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
WETH_DEPOSIT_ABI = [
    {
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


@pytest.fixture(scope="module")
def web3():
    if os.environ.get("RUN_FORK_TESTS") != "1":
        pytest.skip("set RUN_FORK_TESTS=1 to run fork tests")
    rpc_url = os.environ.get("MAINNET_RPC_URL") or DEFAULT_RPC_URL
    anvil = shutil.which("anvil")
    if not anvil:
        pytest.fail("fork tests require Anvil")

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen(
        [
            anvil,
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--chain-id",
            "1",
            "--fork-url",
            rpc_url,
            "--fork-block-number",
            str(FORK_BLOCK),
            "--accounts",
            "1",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        local_web3 = Web3(
            Web3.HTTPProvider(
                f"http://127.0.0.1:{port}", request_kwargs={"timeout": 20}
            )
        )
        timeout = time.monotonic() + 90
        while time.monotonic() < timeout:
            if process.poll() is not None:
                pytest.fail("Anvil could not start; check the fork RPC and block")
            if local_web3.is_connected():
                break
            time.sleep(0.25)
        else:
            pytest.fail("Anvil did not become ready within 90 seconds")

        assert local_web3.eth.chain_id == 1
        assert local_web3.eth.block_number == FORK_BLOCK
        assert local_web3.eth.get_code(WETH)
        assert local_web3.eth.get_code(USDC)
        yield local_web3
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


@pytest.fixture(scope="module")
def funded_account(web3):
    account = web3.eth.account.create()
    faucet = web3.eth.accounts[0]
    weth = web3.eth.contract(address=WETH, abi=WETH_DEPOSIT_ABI)

    receipt = web3.eth.wait_for_transaction_receipt(
        web3.eth.send_transaction(
            {"from": faucet, "to": account.address, "value": Web3.to_wei(1, "ether")}
        )
    )
    assert receipt["status"] == 1
    receipt = web3.eth.wait_for_transaction_receipt(
        weth.functions.deposit().transact(
            {"from": faucet, "value": Web3.to_wei(1, "ether")}
        )
    )
    assert receipt["status"] == 1
    receipt = web3.eth.wait_for_transaction_receipt(
        weth.functions.transfer(
            account.address, Web3.to_wei(Decimal("0.1"), "ether")
        ).transact({"from": faucet})
    )
    assert receipt["status"] == 1
    assert ERC20Token(web3, WETH).balance_of(account.address) == Decimal("0.1")
    return account


@pytest.fixture
def fork_state(web3, funded_account):
    snapshot = web3.provider.make_request("evm_snapshot", [])["result"]
    try:
        yield web3, funded_account
    finally:
        assert web3.provider.make_request("evm_revert", [snapshot])["result"]


def test_approve(fork_state):
    web3, account = fork_state
    weth = ERC20Token(web3, WETH)
    router = UniswapV2Router(web3)

    receipt = weth.approve(
        router.contract.address, Decimal("0.02"), account.address, account.key.hex()
    )

    assert receipt["status"] == 1
    assert weth.allowance(account.address, router.contract.address) == Decimal("0.02")


def test_transfer(fork_state):
    web3, account = fork_state
    weth = ERC20Token(web3, WETH)
    recipient = web3.eth.account.create().address
    sender_before = weth.balance_of(account.address)
    recipient_before = weth.balance_of(recipient)

    receipt = weth.transfer(
        recipient, Decimal("0.01"), account.address, account.key.hex()
    )

    assert receipt["status"] == 1
    assert weth.balance_of(account.address) == sender_before - Decimal("0.01")
    assert weth.balance_of(recipient) == recipient_before + Decimal("0.01")


def test_v2_swap(fork_state):
    web3, account = fork_state
    weth = ERC20Token(web3, WETH)
    usdc = ERC20Token(web3, USDC)
    router = UniswapV2Router(web3)
    amount_in = Decimal("0.01")
    approval = weth.approve(
        router.contract.address, amount_in, account.address, account.key.hex()
    )
    assert approval["status"] == 1
    weth_before = weth.balance_of(account.address)
    usdc_before = usdc.balance_of(account.address)

    receipt = router.swap_exact_tokens_for_tokens(
        amount_in=amount_in,
        amount_out_min=Decimal("0.01"),
        path=[WETH, USDC],
        to=account.address,
        account=account.address,
        private_key=account.key.hex(),
        deadline=web3.eth.get_block("latest")["timestamp"] + 300,
    )

    assert receipt["status"] == 1
    assert weth.balance_of(account.address) == weth_before - amount_in
    assert usdc.balance_of(account.address) > usdc_before


def test_v3_swap(fork_state):
    web3, account = fork_state
    weth = ERC20Token(web3, WETH)
    usdc = ERC20Token(web3, USDC)
    router = UniswapV3Router(web3)
    amount_in = Decimal("0.01")
    approval = weth.approve(
        router.contract.address, amount_in, account.address, account.key.hex()
    )
    assert approval["status"] == 1
    weth_before = weth.balance_of(account.address)
    usdc_before = usdc.balance_of(account.address)

    receipt = router.exact_input_single(
        amount_in=amount_in,
        amount_out_min=Decimal("0.01"),
        token_in=WETH,
        token_out=USDC,
        fee=500,
        recipient=account.address,
        account=account.address,
        private_key=account.key.hex(),
        deadline=web3.eth.get_block("latest")["timestamp"] + 300,
    )

    assert receipt["status"] == 1
    assert weth.balance_of(account.address) == weth_before - amount_in
    assert usdc.balance_of(account.address) > usdc_before


def test_v2_swap_for_exact_output(fork_state):
    web3, account = fork_state
    weth = ERC20Token(web3, WETH)
    usdc = ERC20Token(web3, USDC)
    router = UniswapV2Router(web3)
    amount_out = Decimal("1")
    amount_in_max = Decimal("0.01")
    approval = weth.approve(
        router.contract.address, amount_in_max, account.address, account.key.hex()
    )
    assert approval["status"] == 1
    weth_before = weth.balance_of(account.address)
    usdc_before = usdc.balance_of(account.address)

    receipt = router.swap_tokens_for_exact_tokens(
        amount_out=amount_out,
        amount_in_max=amount_in_max,
        path=[WETH, USDC],
        to=account.address,
        account=account.address,
        private_key=account.key.hex(),
        deadline=web3.eth.get_block("latest")["timestamp"] + 300,
    )

    assert receipt["status"] == 1
    weth_after = weth.balance_of(account.address)
    assert weth_before - amount_in_max <= weth_after < weth_before
    assert usdc.balance_of(account.address) == usdc_before + amount_out


def test_v3_swap_for_exact_output(fork_state):
    web3, account = fork_state
    weth = ERC20Token(web3, WETH)
    usdc = ERC20Token(web3, USDC)
    router = UniswapV3Router(web3)
    amount_out = Decimal("1")
    amount_in_max = Decimal("0.01")
    approval = weth.approve(
        router.contract.address, amount_in_max, account.address, account.key.hex()
    )
    assert approval["status"] == 1
    weth_before = weth.balance_of(account.address)
    usdc_before = usdc.balance_of(account.address)

    receipt = router.exact_output_single(
        amount_out=amount_out,
        amount_in_max=amount_in_max,
        token_in=WETH,
        token_out=USDC,
        fee=500,
        recipient=account.address,
        account=account.address,
        private_key=account.key.hex(),
        deadline=web3.eth.get_block("latest")["timestamp"] + 300,
    )

    assert receipt["status"] == 1
    weth_after = weth.balance_of(account.address)
    assert weth_before - amount_in_max <= weth_after < weth_before
    assert usdc.balance_of(account.address) == usdc_before + amount_out
