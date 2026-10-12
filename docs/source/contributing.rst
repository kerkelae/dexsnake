Contributing
============

Follow these instructions when making changes to the code.

Code style
----------

Use four spaces for indentation, ``snake_case`` for functions and variables,
and ``PascalCase`` for classes. Add comments only for non-obvious behavior.
Ruff handles formatting and import order.

Format the code by running:

.. code-block:: console

   python -m ruff check --fix --select I .
   python -m ruff format .

Development environment
-----------------------

Install the package and development dependencies in your environment:

.. code-block:: console

   python -m pip install -e .
   python -m pip install -r requirements-dev.txt

Install `Anvil <https://getfoundry.sh/getting-started/installation/>`_ and set
the environment variable ``WEB3_RPC_URL`` to an Ethereum mainnet RPC that can
read block 20,000,000. The fork tests send transactions only to local Anvil.

Tests
-----

After making changes, check them by running:

.. code-block:: console

   python -m pytest
   python -m ruff check .
   python -m ruff format --check .

Documentation
-------------

Build the documentation by running:

.. code-block:: console

   sphinx-build -b html docs/source docs/_build/html

This generates a local copy at ``docs/_build/html/index.html``.
