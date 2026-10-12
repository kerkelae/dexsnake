Contributing
============

Install the package and development tools separately:

.. code-block:: console

   python -m pip install -e .
   python -m pip install -r requirements-dev.txt

Install `Anvil <https://getfoundry.sh/getting-started/installation/>`_ and set
the environment variable ``WEB3_RPC_URL`` to an Ethereum mainnet RPC that can
read block 20,000,000.
The fork tests send transactions only to local Anvil.

.. code-block:: console

   python -m ruff check --fix --select I .
   python -m ruff format .
   python -m pytest
   python -m ruff check .
