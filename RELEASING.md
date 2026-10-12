# Releasing Dexsnake

While Dexsnake is below version 1.0, use `0.MINOR.PATCH`: increment `MINOR` for new or incompatible API changes and `PATCH` for fixes. The version in `pyproject.toml` is the source of truth. Release tags use `v<version>`, for example `v0.1.0`. Write release notes in the GitHub Release.

## Each release

1. Update the version in `pyproject.toml` to a version that has not been published on PyPI. Merge the change into `main` and wait for CI to pass.
2. Create and publish a GitHub Release from that commit, using its matching `v<version>` tag and concise release notes. Leave the GitHub prerelease option unchecked; the workflow skips prereleases.
3. Confirm that the workflow uploaded both the wheel and source distribution to [PyPI](https://pypi.org/project/Dexsnake/).

The `release.yml` workflow publishes through the `pypi` GitHub environment and PyPI Trusted Publishing.
