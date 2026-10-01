Getting Started
===============

To begin using Dexsnake, the first step is to connect with a provider and initialize a
Web3 instance.

.. tip::
   
   For more information, please see `the web3.py documentation
   <https://web3py.readthedocs.io/en/stable/providers.html>`_.

Connecting to the Blockchain
############################

The provider facilitates the interaction with the blockchain. The most common ways to
connect to the blockchain are:

- **IPC**: Ideal when your application is hosted on the same physical or virtual
  machine as the blockchain node. IPC provides the quickest communication with the node.

- **WebSocket**: Useful when the application needs a persistent connection or
  real-time updates from the node.

- **HTTP**: This is a versatile and widely used method that offers extensive
  compatibility with various nodes. It's particularly useful in situations where the
  simplicity of setup is a priority.

The Python snippet below initializes how to configure each type of provider and
initialize a Web3 instance.

.. code-block:: python

   from web3 import Web3
   
   # IPC
   provider = Web3.IPCProvider("/my/node/ipc/path")
   
   # WebSocket
   provider = Web3.LegacyWebSocketProvider("wss://my-node-url")
   
   # HTTP
   provider = Web3.HTTPProvider("https://my-node-url")
   
   # Initialize the Web3 instance
   web3 = Web3(provider)

After configuring the provider and initializing the Web3 instance, you are ready to use
Dexsnake.

.. note::
   
   Dexsnake uses the initialized Web3 instance to determine which blockchain is used and
   automatically selects the corresponding smart contract addresses.

Making Transactions
###################

While you can read data on the blockchain using just a provider, you need to make
transactions on the blockchain to make trades. The account address identifies the
sender; its private key signs transactions. Keep the key secret and never commit or
print it. One way to load it is through an environment variable:

.. code-block:: python

   import os

   private_key = os.environ["WEB3_PRIVATE_KEY"]
