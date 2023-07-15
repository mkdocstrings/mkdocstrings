---
title: Getting started with Insiders
---

# Getting started with Insiders

*mkdocstrings Insiders* is a compatible drop-in replacement for *mkdocstrings*,
and can be installed similarly using `pip` or `git`.
Note that in order to access the Insiders  repository,
you need to [become an eligible sponsor] of @pawamoy on GitHub.

  [become an eligible sponsor]: index.md#how-to-become-a-sponsor

## Installation

### with PyPI Insiders

[PyPI Insiders](https://pawamoy.github.io/pypi-insiders/)
is a tool that helps you keep up-to-date versions
of Insiders projects in the PyPI index of your choice
(self-hosted, Google registry, Artifactory, etc.).

See [how to install it](https://pawamoy.github.io/pypi-insiders/#installation)
and [how to use it](https://pawamoy.github.io/pypi-insiders/#usage).

### with pip (ssh/https)

*mkdocstrings Insiders* can be installed with `pip` [using SSH][using ssh]:

```bash
pip install git+ssh://git@github.com/pawamoy-insiders/mkdocstrings.git
```

  [using ssh]: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

Or using HTTPS:

```bash
pip install git+https://${GH_TOKEN}@github.com/pawamoy-insiders/mkdocstrings.git
```

>? NOTE: **How to get a GitHub personal access token**  
> The `GH_TOKEN` environment variable is a GitHub token.
> It can be obtained by creating a [personal access token] for
> your GitHub account. It will give you access to the Insiders repository,
> programmatically, from the command line or GitHub Actions workflows:
> 
> 1.  Go to https://github.com/settings/tokens
> 2.  Click on [Generate a new token]
> 3.  Enter a name and select the [`repo`][scopes] scope
> 4.  Generate the token and store it in a safe place
> 
>   [personal access token]: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
>   [Generate a new token]: https://github.com/settings/tokens/new
>   [scopes]: https://docs.github.com/en/developers/apps/scopes-for-oauth-apps#available-scopes
> 
> Note that the personal access
> token must be kept secret at all times, as it allows the owner to access your
> private repositories.

### with pip (self-hosted)

Self-hosting the Insiders package makes it possible to depend on *mkdocstrings* normally,
while transparently downloading and installing the Insiders version locally.
It means that you can specify your dependencies normally, and your contributors without access
to Insiders will get the public version, while you get the Insiders version on your machine.

WARNING: **Limitation**  
With this method, there is no way to force the installation of an Insiders version
rather than a public version. If there is a public version that is more recent
than your self-hosted Insiders version, the public version will take precedence.
Remember to regularly update your self-hosted versions by uploading latest distributions.

You can build the distributions for Insiders yourself, by cloning the repository
and using [build] to build the distributions,
or you can download them from our [GitHub Releases].
You can upload these distributions to a private PyPI-like registry
([Artifactory], [Google Cloud], [pypiserver], etc.)
with [Twine]:

  [build]: https://pypi.org/project/build/
  [Artifactory]: https://jfrog.com/help/r/jfrog-artifactory-documentation/pypi-repositories
  [Google Cloud]: https://cloud.google.com/artifact-registry/docs/python
  [pypiserver]: https://pypi.org/project/pypiserver/
  [Github Releases]: https://github.com/pawamoy-insiders/mkdocstrings/releases
  [Twine]: https://pypi.org/project/twine/

```bash
# download distributions in ~/dists, then upload with:
twine upload --repository-url https://your-private-index.com ~/dists/*
```

<small>You might also need to provide a username and password/token to authenticate against the registry.
Please check [Twine's documentation][twine docs].</small>

  [twine docs]: https://twine.readthedocs.io/en/stable/

You can then configure pip (or other tools) to look for packages into your package index.
For example, with pip:

```bash
pip config set global.extra-index-url https://your-private-index.com/simple
```

Note that the URL might differ depending on whether your are uploading a package (with Twine)
or installing a package (with pip), and depending on the registry you are using (Artifactory, Google Cloud, etc.).
Please check the documentation of your registry to learn how to configure your environment.

**We kindly ask that you do not upload the distributions to public registries,
as it is against our [Terms of use](../#terms).**

>? TIP: **Full example with `pypiserver`**  
> In this example we use [pypiserver] to serve a local PyPI index.
>
> ```bash
> pip install --user pypiserver
> # or pipx install pypiserver
>
> # create a packages directory
> mkdir -p ~/.local/pypiserver/packages
>
> # run the pypi server without authentication
> pypi-server run -p 8080 -a . -P . ~/.local/pypiserver/packages &
> ```
>
> We can configure the credentials to access the server in [`~/.pypirc`][pypirc]:
>
>   [pypirc]: https://packaging.python.org/en/latest/specifications/pypirc/
>
> ```ini title=".pypirc"
> [distutils]
> index-servers =
>     local
>
> [local]
> repository: http://localhost:8080
> username:
> password:
> ```
>
> We then clone the Insiders repository, build distributions and upload them to our local server:
>
> ```bash
> # clone the repository
> git clone git@github.com:pawamoy-insiders/mkdocstrings
> cd mkdocstrings
>
> # install build
> pip install --user build
> # or pipx install build
>
> # checkout latest tag
> git checkout $(git describe --tags --abbrev=0)
>
> # build the distributions
> pyproject-build
>
> # upload them to our local server
> twine upload -r local dist/* --skip-existing
> ```
>
> Finally, we configure pip, and for example [PDM][pdm], to use our local index to find packages:
>
> ```bash
> pip config set global.extra-index-url http://localhost:8080/simple
> pdm config pypi.extra.url http://localhost:8080/simple
> ```
>
>   [pdm]: https://pdm.fming.dev/latest/
>
> Now when running `pip install mkdocstrings`,
> or resolving dependencies with PDM,
> both tools will look into our local index and find the Insiders version.
> **Remember to update your local index regularly!**

### with git

Of course, you can use *mkdocstrings Insiders* directly from `git`:

```
git clone git@github.com:pawamoy-insiders/mkdocstrings
```

When cloning from `git`, the package must be installed:

```
pip install -e mkdocstrings
```

## Upgrading

When upgrading Insiders, you should always check the version of *mkdocstrings*
which makes up the first part of the version qualifier. For example, a version like
`8.x.x.4.x.x` means that Insiders `4.x.x` is currently based on `8.x.x`.

If the major version increased, it's a good idea to consult the [changelog]
and go through the steps to ensure your configuration is up to date and
all necessary changes have been made.

  [changelog]: ./changelog.md
