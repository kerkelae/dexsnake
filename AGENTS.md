# Local development

Use the `dexsnake` conda environment. Install Python and pip there with
`conda install -n dexsnake python=3.14 pip`, then run `conda activate dexsnake`
before following `docs/source/contributing.rst`.

Set its fork RPC with
`conda env config vars set -n dexsnake WEB3_RPC_URL=<mainnet-archive-rpc>` and
reactivate the environment after changing it.
