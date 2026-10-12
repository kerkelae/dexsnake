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

Code style
----------

Follow the surrounding code, keep changes focused, and comment only where the
behavior is not obvious. Ruff handles formatting and import order:

.. code-block:: console

   python -m ruff check --fix --select I .
   python -m ruff format .

Before opening a pull request, run:

.. code-block:: console

   python -m pytest
   python -m ruff check .
   python -m ruff format --check .
