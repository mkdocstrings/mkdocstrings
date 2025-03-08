---
title: Getting started with Insiders
---

# Getting started with Insiders

*mkdocstrings Insiders* is a compatible drop-in replacement for *mkdocstrings*, and can be installed similarly using `pip` or `git`. Note that in order to access the Insiders repository, you need to [become an eligible sponsor][] of @pawamoy on GitHub.

## Installation

### with the `insiders` tool

[`insiders`][insiders-tool] is a tool that helps you keep up-to-date versions of Insiders projects in the PyPI index of your choice (self-hosted, Google registry, Artifactory, etc.).

**We kindly ask that you do not upload the distributions to public registries, as it is against our [Terms of use][].**

### with pip (ssh/https)

*mkdocstrings Insiders* can be installed with `pip` [using SSH][install-pip-ssh]:

```bash
pip install git+ssh://git@github.com/pawamoy-insiders/mkdocstrings.git
```

Or using HTTPS:

```bash
pip install git+https://${GH_TOKEN}@github.com/pawamoy-insiders/mkdocstrings.git
```

>? NOTE: **How to get a GitHub personal access token?** The `GH_TOKEN` environment variable is a GitHub token. It can be obtained by creating a [personal access token][github-pat] for your GitHub account. It will give you access to the Insiders repository, programmatically, from the command line or GitHub Actions workflows:
>
> 1.  Go to https://github.com/settings/tokens
> 2.  Click on [Generate a new token][github-pat-new]
> 3.  Enter a name and select the [`repo`][scopes] scope
> 4.  Generate the token and store it in a safe place
>
> Note that the personal access token must be kept secret at all times, as it allows the owner to access your private repositories.

### with Git

Of course, you can use *mkdocstrings Insiders* directly using Git:

```
git clone git@github.com:pawamoy-insiders/mkdocstrings
```

When cloning with Git, the package must be installed:

```
pip install -e mkdocstrings
```

## Upgrading

When upgrading Insiders, you should always check the version of *mkdocstrings* which makes up the first part of the version qualifier. For example, a version like `8.x.x.4.x.x` means that Insiders `4.x.x` is currently based on `8.x.x`.

If the major version increased, it's a good idea to consult the [changelog][] and go through the steps to ensure your configuration is up to date and all necessary changes have been made.

[become an eligible sponsor]: ./index.md#how-to-become-a-sponsor
[changelog]: ./changelog.md
[github-pat]: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
[github-pat-new]: https://github.com/settings/tokens/new
[insiders-tool]: https://pawamoy.github.io/insiders-project/
[install-pip-ssh]: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
[scopes]: https://docs.github.com/en/developers/apps/scopes-for-oauth-apps#available-scopes
[terms of use]: ./index.md#terms
