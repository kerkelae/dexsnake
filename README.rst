Dexsnake
========

Dexsnake is a lightweight Python package that makes it easy to make trades on
decentralized exchanges (DEXs) like `Uniswap <https://uniswap.org/>`_. The package is
designed for Python developers, quants, data scientists, algorithmic traders, and others
who are used to working in Python but may not have in-depth knowledge about blockchains
and decentralized apps. The code is organized to closely follow the structure of the
smart contracts, ensuring that by using Dexsnake, users also gain an understanding of
the underlying protocols.

Installation
############

.. note::

   Dexsnake is under active development. Its API may change before version 1.0.
   Review transaction parameters carefully before trading with real funds.

The most recent release can be installed with `pip <https://pip.pypa.io/>`_:

.. code-block::

   pip install dexsnake

The development version can be installed from GitHub:

.. code-block::

   pip install git+https://github.com/kerkelae/dexsnake.git

Development
###########

Install Python and pip in the ``dexsnake`` conda environment, then install the
package and development tools separately:

.. code-block::

   conda install -n dexsnake python=3.14 pip
   conda activate dexsnake
   pip install -e .
   pip install -r requirements-dev.txt

Fork tests
##########

Install `Anvil <https://getfoundry.sh/getting-started/installation/>`_ separately.
The tests fork Ethereum block 20,000,000 using the public
`Reth RPC <https://reth.rs/run/overview/>`_ by default and send transactions only
to local Anvil. CI runs the same tests in a separate job:

.. code-block::

   RUN_FORK_TESTS=1 pytest -m fork

Set ``MAINNET_RPC_URL`` to use another RPC that can read that block.
