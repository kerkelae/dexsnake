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

For the fork tests, install `Anvil <https://getfoundry.sh/getting-started/installation/>`_
and set the environment variable ``WEB3_RPC_URL`` to an Ethereum mainnet RPC
that can read block 20,000,000. The fork tests send transactions only to local
Anvil.

Tests
-----

Run the offline tests without Anvil or an RPC URL:

.. code-block:: console

   python -m pytest -m "not fork"

Run the fork tests after installing Anvil and setting ``WEB3_RPC_URL`` as described
above:

.. code-block:: console

   python -m pytest -m fork

The full test suite includes both groups and therefore also requires Anvil and the
archive RPC:

.. code-block:: console

   python -m pytest

Documentation
-------------

Build the documentation by running:

.. code-block:: console

   sphinx-build -b html docs/source docs/_build/html

This generates a local copy at ``docs/_build/html/index.html``.
