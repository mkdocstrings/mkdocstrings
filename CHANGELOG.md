# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [0.30.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.30.0) - 2025-07-23

<small>[Compare with 0.29.1](https://github.com/mkdocstrings/mkdocstrings/compare/0.29.1...0.30.0)</small>

### Features

- Add `data-skip-inventory` boolean attribute for elements to skip registration in local inventory ([f856160](https://github.com/mkdocstrings/mkdocstrings/commit/f856160b03b2c27e1d75fdf4f315c273cb9d9247) by Bartosz Sławecki). [Issue-671](https://github.com/mkdocstrings/mkdocstrings/issues/671), [PR-774](https://github.com/mkdocstrings/mkdocstrings/pull/774)
- Add I18N support (translations) ([2b4ed54](https://github.com/mkdocstrings/mkdocstrings/commit/2b4ed541bc707e55d959092d950ebeecc4fbd136) by Nyuan Zhang). [PR-645](https://github.com/mkdocstrings/mkdocstrings/pull/645), Co-authored-by: Timothée Mazzucotelli <dev@pawamoy.fr>

## [0.29.1](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.29.1) - 2025-03-31

<small>[Compare with 0.29.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.29.0...0.29.1)</small>

### Dependencies

- Remove unused typing-extensions dependency ([ba98661](https://github.com/mkdocstrings/mkdocstrings/commit/ba98661b50e2cde19d8696d6c8ceecdbb49ce83f) by Timothée Mazzucotelli).

### Bug Fixes

- Ignore invalid inventory lines ([81caff5](https://github.com/mkdocstrings/mkdocstrings/commit/81caff5ff76f1a6606da9d2980e81ae9d2e02246) by Josh Mitchell). [PR-748](https://github.com/mkdocstrings/mkdocstrings/pull/748)

### Code Refactoring

- Rename loggers to "mkdocstrings" ([1a98040](https://github.com/mkdocstrings/mkdocstrings/commit/1a980402c39728ce265d8998b396c34bf76a113d) by Timothée Mazzucotelli).

## [0.29.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.29.0) - 2025-03-10

<small>[Compare with 0.28.3](https://github.com/mkdocstrings/mkdocstrings/compare/0.28.3...0.29.0)</small>

**This is the last version before v1!**

### Build

- Depend on MkDocs 1.6 ([11bc400](https://github.com/mkdocstrings/mkdocstrings/commit/11bc400ab7089a47755f24a790c08f2f904c570b) by Timothée Mazzucotelli).

### Features

- Support rendering backlinks through handlers ([d4c7b9c](https://github.com/mkdocstrings/mkdocstrings/commit/d4c7b9c42f2de5df234c1ffefae0405a120e383c) by Timothée Mazzucotelli). [Issue-723](https://github.com/mkdocstrings/mkdocstrings/issues/723), [Issue-mkdocstrings-python-153](https://github.com/mkdocstrings/python/issues/153), [PR-739](https://github.com/mkdocstrings/mkdocstrings/pull/739)

### Code Refactoring

- Save and forward titles to autorefs ([f49fb29](https://github.com/mkdocstrings/mkdocstrings/commit/f49fb29582714795ca03febf1ee243aa2992917e) by Timothée Mazzucotelli).
- Use a combined event (each split with a different priority) for `on_env` ([8d1dd75](https://github.com/mkdocstrings/mkdocstrings/commit/8d1dd754b4babd3c4f9e6c1d8856be57fe4ba9ea) by Timothée Mazzucotelli).

## [0.28.3](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.28.3) - 2025-03-08

<small>[Compare with 0.28.2](https://github.com/mkdocstrings/mkdocstrings/compare/0.28.2...0.28.3)</small>

### Deprecations

All public objects must now be imported from the top-level `mkdocstrings` module. Importing from submodules is deprecated, and will raise errors starting with v1. This should be the last deprecation before v1.

### Build

- Make `python` extra depend on latest mkdocstrings-python (1.16.2) ([ba9003e](https://github.com/mkdocstrings/mkdocstrings/commit/ba9003e96c8e5e01900743d5c464cbd228d732f4) by Timothée Mazzucotelli).

### Code Refactoring

- Finish exposing/hiding public/internal objects ([0723fc2](https://github.com/mkdocstrings/mkdocstrings/commit/0723fc25fdf5d45bc3b949f370712a706b85fbab) by Timothée Mazzucotelli).
- Re-expose public API in the top-level `mkdocstrings` module ([e66e080](https://github.com/mkdocstrings/mkdocstrings/commit/e66e08096d45f6790492d9a0b767d512e42f67a9) by Timothée Mazzucotelli).
- Move modules to internal folder ([23fe23f](https://github.com/mkdocstrings/mkdocstrings/commit/23fe23f11011d0470a6342ca85e060e5ac2b6bd6) by Timothée Mazzucotelli).

## [0.28.2](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.28.2) - 2025-02-24

<small>[Compare with 0.28.1](https://github.com/mkdocstrings/mkdocstrings/compare/0.28.1...0.28.2)</small>

### Build

- Depend on mkdocs-autorefs >= 1.4 ([2c22bdc](https://github.com/mkdocstrings/mkdocstrings/commit/2c22bdc49f6bf5600aefd5ec711747686fda96a8) by Timothée Mazzucotelli).

## [0.28.1](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.28.1) - 2025-02-14

<small>[Compare with 0.28.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.28.0...0.28.1)</small>

### Bug Fixes

- Renew MkDocs' `relpath` processor instead of using same instance ([4ab180d](https://github.com/mkdocstrings/mkdocstrings/commit/4ab180d01964c3ef8005cd72c8d91ba3fd241e27) by Timothée Mazzucotelli). [Issue-mkdocs-3919](https://github.com/mkdocs/mkdocs/issues/3919)

## [0.28.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.28.0) - 2025-02-03

<small>[Compare with 0.27.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.27.0...0.28.0)</small>

### Breaking Changes

Although the following changes are "breaking" in terms of public API, we didn't find any public use of these classes and methods on GitHub.

- `mkdocstrings.extension.AutoDocProcessor.__init__(parser)`: *Parameter was removed*
- `mkdocstrings.extension.AutoDocProcessor.__init__(md)`: *Positional parameter was moved*
- `mkdocstrings.extension.AutoDocProcessor.__init__(config)`: *Parameter was removed*
- `mkdocstrings.extension.AutoDocProcessor.__init__(handlers)`: *Parameter kind was changed*: `positional or keyword` -> `keyword-only`
- `mkdocstrings.extension.AutoDocProcessor.__init__(autorefs)`: *Parameter kind was changed*: `positional or keyword` -> `keyword-only`
- `mkdocstrings.extension.MkdocstringsExtension.__init__(config)`: *Parameter was removed*
- `mkdocstrings.extension.MkdocstringsExtension.__init__(handlers)`: *Positional parameter was moved*
- `mkdocstrings.extension.MkdocstringsExtension.__init__(autorefs)`: *Positional parameter was moved*
- `mkdocstrings.handlers.base.Handlers.__init__(config)`: *Parameter was removed*
- `mkdocstrings.handlers.base.Handlers.__init__(theme)`: *Parameter was added as required*
- `mkdocstrings.handlers.base.Handlers.__init__(default)`: *Parameter was added as required*
- `mkdocstrings.handlers.base.Handlers.__init__(inventory_project)`: *Parameter was added as required*
- `mkdocstrings.handlers.base.Handlers.__init__(tool_config)`: *Parameter was added as required*

Similarly, the following parameters were renamed, but the methods are only called from our own code, using positional arguments.

- `mkdocstrings.handlers.base.BaseHandler.collect(config)`: *Parameter was renamed `options`*
- `mkdocstrings.handlers.base.BaseHandler.render(config)`: *Parameter was renamed `options`*

Finally, the following method was removed, but this is again taken into account in our own code:

- `mkdocstrings.handlers.base.BaseHandler.get_anchors`: *Public object was removed*

For these reasons, and because we're still in v0, we do not bump to v1 yet. See following deprecations.

### Deprecations

*mkdocstrings* 0.28 will start emitting these deprecations warnings:

> The `handler` argument is deprecated. The handler name must be specified as a class attribute.

Previously, the `get_handler` function would pass a `handler` (name) argument to the handler constructor. This name must now be set on the handler's class directly.

```python
class MyHandler:
    name = "myhandler"
```

> The `domain` attribute must be specified as a class attribute.

The `domain` class attribute on handlers is now mandatory and cannot be an empty string.

```python
class MyHandler:
    domain = "mh"
```

> The `theme` argument must be passed as a keyword argument.

This argument could previously be passed as a positional argument (from the `get_handler` function), and must now be passed as a keyword argument.

> The `custom_templates` argument must be passed as a keyword argument.

Same as for `theme`, but with `custom_templates`.

> The `mdx` argument must be provided (as a keyword argument).

The `get_handler` function now receives a `mdx` argument, which it must forward to the handler constructor and then to the base handler, either explicitly or through `**kwargs`:

=== "Explicitly"

    ```python
    def get_handler(..., mdx, ...):
        return MyHandler(..., mdx=mdx, ...)


    class MyHandler:
        def __init__(self, ..., mdx, ...):
            super().__init__(..., mdx=mdx, ...)
    ```

=== "Through `**kwargs`"

    ```python
    def get_handler(..., **kwargs):
        return MyHandler(..., **kwargs)


    class MyHandler:
        def __init__(self, ..., **kwargs):
            super().__init__(**kwargs)
    ```

In the meantime we still retrieve this `mdx` value at a different moment, by reading it from the MkDocs configuration.

> The `mdx_config` argument must be provided (as a keyword argument).

Same as for `mdx`, but with `mdx_config`.

> mkdocstrings v1 will stop handling 'import' in handlers configuration. Instead your handler must define a `get_inventory_urls` method that returns a list of URLs to download.

Previously, mkdocstrings would pop the `import` key from a handler's configuration to download each item (URLs). Items could be strings, or dictionaries with a `url` key. Now mkdocstrings gives back control to handlers, which must store this inventory configuration within them, and expose it again through a `get_inventory_urls` method. This method returns a list of tuples: an URL, and a dictionary of options that will be passed again to their `load_inventory` method. Handlers have now full control over the "inventory" setting.

```python
from copy import deepcopy


def get_handler(..., handler_config, ...):
    return MyHandler(..., config=handler_config, ...)


class MyHandler:
    def __init__(self, ..., config, ...):
        self.config = config

    def get_inventory_urls(self):
        config = deepcopy(self.config["import"])
        return [(inv, {}) if isinstance(inv, str) else (inv.pop("url"), inv) for inv in config]
```

Changing the name of the key (for example from `import` to `inventories`) involves a change in user configuration, and both keys will have to be supported by your handler for some time.

```python
def get_handler(..., handler_config, ...):
    if "inventories" not in handler_config and "import" in handler_config:
        warn("The 'import' key is renamed 'inventories'", FutureWarning)
        handler_config["inventories"] = handler_config.pop("import")
    return MyHandler(..., config=handler_config, ...)
```

> Setting a fallback anchor function is deprecated and will be removed in a future release.

This comes from mkdocstrings and mkdocs-autorefs, and will disappear with mkdocstrings v0.28.

> mkdocstrings v1 will start using your handler's `get_options` method to build options instead of merging the global and local options (dictionaries).

Handlers must now store their own global options (in an instance attribute), and implement a `get_options` method that receives `local_options` (a dict) and returns combined options (dict or custom object). These combined options are then passed to `collect` and `render`, so that these methods can use them right away.

```python
def get_handler(..., handler_config, ...):
    return MyHandler(..., config=handler_config, ...)


class MyHandler:
    def __init__(self, ..., config, ...):
        self.config = config

    def get_options(local_options):
        return {**self.default_options, **self.config["options"], **local_options}
```

> The `update_env(md)` parameter is deprecated. Use `self.md` instead.

Handlers can remove the `md` parameter from their `update_env` method implementation, and use `self.md` instead, if they need it.

> No need to call `super().update_env()` anymore.

Handlers don't have to call the parent `update_env` method from their own implementation anymore, and can just drop the call.

>  The `get_anchors` method is deprecated. Declare a `get_aliases` method instead, accepting a string (identifier) instead of a collected object.

Previously, handlers would implement a `get_anchors` method that received a data object (typed `CollectorItem`) to return aliases for this object. This forced mkdocstrings to collect this object through the handler's `collect` method, which then required some logic with "fallback config" as to prevent unwanted collection. mkdocstrings gives back control to handlers and now calls `get_aliases` instead, which accepts an `identifier` (string) and lets the handler decide how to return aliases for this identifier. For example, it can replicate previous behavior by calling its own `collect` method with its own "fallback config", or do something different (cache lookup, etc.).

```python
class MyHandler:
    def get_aliases(identifier):
        try:
            obj = self.collect(identifier, self.fallback_config)
            # or obj = self._objects_cache[identifier]
        except CollectionError:  # or KeyError
            return ()
        return ...  # previous logic in `get_anchors`
```

> The `config_file_path` argument in `get_handler` functions is deprecated. Use `tool_config.get('config_file_path')` instead.

The `config_file_path` argument is now deprecated and only passed to `get_handler` functions if they accept it. If you used it to compute a "base directory", you can now use the `tool_config` argument instead, which is the configuration of the SSG tool in use (here MkDocs):

```python
base_dir = Path(tool_config.config_file_path or "./mkdocs.yml").parent
```

**Most of these warnings will disappear with the next version of mkdocstrings-python.**

### Bug Fixes

- Update handlers in JSON schema to be an object instead of an array ([3cf7d51](https://github.com/mkdocstrings/mkdocstrings/commit/3cf7d51704378adc50d4ea50080aacae39e0e731) by Matthew Messinger). [Issue-733](https://github.com/mkdocstrings/mkdocstrings/issues/733), [PR-734](https://github.com/mkdocstrings/mkdocstrings/pull/734)
- Fix broken table of contents when nesting autodoc instructions ([12c8f82](https://github.com/mkdocstrings/mkdocstrings/commit/12c8f82e9a959ce32cada09f0d2b5c651a705fdb) by Timothée Mazzucotelli). [Issue-348](https://github.com/mkdocstrings/mkdocstrings/issues/348)

### Code Refactoring

- Pass `config_file_path` to `get_handler` if it expects it ([8c476ee](https://github.com/mkdocstrings/mkdocstrings/commit/8c476ee0b82c09a5b20d7a773ecaf4be17b9e4d1) by Timothée Mazzucotelli).
- Give back inventory control to handlers ([b84653f](https://github.com/mkdocstrings/mkdocstrings/commit/b84653f2b175824c73bd0291fafff8343ba80125) by Timothée Mazzucotelli). [Related-to-issue-719](https://github.com/mkdocstrings/mkdocstrings/issues/719)
- Give back control to handlers on how they want to handle global/local options ([c00de7a](https://github.com/mkdocstrings/mkdocstrings/commit/c00de7a42b9072cbaa47ecbf18e3e15a6d5ab634) by Timothée Mazzucotelli). [Issue-719](https://github.com/mkdocstrings/mkdocstrings/issues/719)
- Deprecate base handler's `get_anchors` method in favor of `get_aliases` method ([7a668f0](https://github.com/mkdocstrings/mkdocstrings/commit/7a668f0f731401b07123bd02aafbbfc55cd24c0d) by Timothée Mazzucotelli).
- Register all identifiers of rendered objects into autorefs ([434d8c7](https://github.com/mkdocstrings/mkdocstrings/commit/434d8c7cd1e3edbdb9d4c45a9b44b290b19d88f1) by Timothée Mazzucotelli).
- Use mkdocs-get-deps' download utility to remove duplicated code ([bb87cd8](https://github.com/mkdocstrings/mkdocstrings/commit/bb87cd833f2333e77cb2c2926aa24a434c97391f) by Timothée Mazzucotelli).
- Clean up data passed down from plugin to extension and handlers ([b8e8703](https://github.com/mkdocstrings/mkdocstrings/commit/b8e87036e0e1ec5c181b4a2ec5931f1a60636a32) by Timothée Mazzucotelli). [PR-726](https://github.com/mkdocstrings/mkdocstrings/pull/726)

## [0.27.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.27.0) - 2024-11-08

<small>[Compare with 0.26.2](https://github.com/mkdocstrings/mkdocstrings/compare/0.26.2...0.27.0)</small>

### Features

- Add support for authentication in inventory file URLs ([1c23c1b](https://github.com/mkdocstrings/mkdocstrings/commit/1c23c1b0fc4a9bdec5e0eb43c8647beab66fec55) by Stefan Mejlgaard). [Issue-707](https://github.com/mkdocstrings/mkdocstrings/issues/707), [PR-710](https://github.com/mkdocstrings/mkdocstrings/pull/710)

### Performance Improvements

- Reduce footprint of template debug messages ([5648e5a](https://github.com/mkdocstrings/mkdocstrings/commit/5648e5aca80a5d8ba9e5456efb36b517b9f3cdeb) by Timothée Mazzucotelli).

### Code Refactoring

- Use %-formatting for logging messages ([0bbb8ca](https://github.com/mkdocstrings/mkdocstrings/commit/0bbb8caddf34b0a4faa0ed6f26e33102dc892fc8) by Timothée Mazzucotelli).

## [0.26.2](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.26.2) - 2024-10-12

<small>[Compare with 0.26.1](https://github.com/mkdocstrings/mkdocstrings/compare/0.26.1...0.26.2)</small>

### Build

- Drop support for Python 3.8 ([f26edeb](https://github.com/mkdocstrings/mkdocstrings/commit/f26edebe01337caa802a98c13240acdd8332a5fa) by Timothée Mazzucotelli).

## [0.26.1](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.26.1) - 2024-09-06

<small>[Compare with 0.26.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.26.0...0.26.1)</small>

### Bug Fixes

- Instantiate config of the autorefs plugin when it is not enabled by the user ([db2ab34](https://github.com/mkdocstrings/mkdocstrings/commit/db2ab3403a95034987d574a517ddc426a4b4e1bd) by Timothée Mazzucotelli). [Issue-autorefs#57](https://github.com/mkdocstrings/autorefs/issues/57)

## [0.26.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.26.0) - 2024-09-02

<small>[Compare with 0.25.2](https://github.com/mkdocstrings/mkdocstrings/compare/0.25.2...0.26.0)</small>

### Build

- Upgrade Python-Markdown lower bound to 3.6 ([28565f9](https://github.com/mkdocstrings/mkdocstrings/commit/28565f97f21bf81b2bc554679c641fba3f639882) by Timothée Mazzucotelli).

### Dependencies

- Depend on mkdocs-autorefs v1 ([33aa573](https://github.com/mkdocstrings/mkdocstrings/commit/33aa573efb17b13e7b9da77e29aeccb3fbddd8e8) by Timothée Mazzucotelli).

### Features

- Allow hooking into autorefs when converting Markdown docstrings ([b63e726](https://github.com/mkdocstrings/mkdocstrings/commit/b63e72691a8f92dd59b56304125de4a19e0d028c) by Timothée Mazzucotelli). [Based-on-PR-autorefs#46](https://github.com/mkdocstrings/autorefs/pull/46)

## [0.25.2](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.25.2) - 2024-07-25

<small>[Compare with 0.25.1](https://github.com/mkdocstrings/mkdocstrings/compare/0.25.1...0.25.2)</small>

### Code Refactoring

- Give precedence to Markdown heading level (`##`) ([2e5f89e](https://github.com/mkdocstrings/mkdocstrings/commit/2e5f89e8cef11e6447425d3700c29558cd6d241b) by Timothée Mazzucotelli).

## [0.25.1](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.25.1) - 2024-05-05

<small>[Compare with 0.25.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.25.0...0.25.1)</small>

### Bug Fixes

- Always descend into sub-headings when re-applying their label ([cb86e08](https://github.com/mkdocstrings/mkdocstrings/commit/cb86e08bbc5e8057393aa1cd7ca29bc2b40ab5eb) by Timothée Mazzucotelli). [Issue-mkdocstrings/python-158](https://github.com/mkdocstrings/python/issues/158)

## [0.25.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.25.0) - 2024-04-27

<small>[Compare with 0.24.3](https://github.com/mkdocstrings/mkdocstrings/compare/0.24.3...0.25.0)</small>

### Features

- Support `once` parameter in logging methods, allowing to log a message only once with a given logger ([1532b59](https://github.com/mkdocstrings/mkdocstrings/commit/1532b59a6efd99fed846cf7edfd0b26525700d3f) by Timothée Mazzucotelli).
- Support blank line between `::: path` and YAML options ([d799d2f](https://github.com/mkdocstrings/mkdocstrings/commit/d799d2f3903bce44fb751f8cf3fb8078d25549da) by Timothée Mazzucotelli). [Issue-450](https://github.com/mkdocstrings/mkdocstrings/issues/450)

### Code Refactoring

- Allow specifying name of template loggers ([c5b5f69](https://github.com/mkdocstrings/mkdocstrings/commit/c5b5f697c83271d961c7ac795412d6b4964ba2b7) by Timothée Mazzucotelli).

## [0.24.3](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.24.3) - 2024-04-05

<small>[Compare with 0.24.2](https://github.com/mkdocstrings/mkdocstrings/compare/0.24.2...0.24.3)</small>

### Bug Fixes

- Support HTML toc labels with Python-Markdown 3.6+ (uncomment code...) ([7fe3e5f](https://github.com/mkdocstrings/mkdocstrings/commit/7fe3e5f28239c08094fb656728369998f52630ea) by Timothée Mazzucotelli).

## [0.24.2](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.24.2) - 2024-04-02

<small>[Compare with 0.24.1](https://github.com/mkdocstrings/mkdocstrings/compare/0.24.1...0.24.2)</small>

### Bug Fixes

- Support HTML toc labels with Python-Markdown 3.6+ ([c0d0090](https://github.com/mkdocstrings/mkdocstrings/commit/c0d009000678a2ccbfb0c8adfeff3dc83845ee41) by Timothée Mazzucotelli). [Issue-mkdocstrings/python-143](https://github.com/mkdocstrings/python/issues/143)

## [0.24.1](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.24.1) - 2024-02-27

<small>[Compare with 0.24.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.24.0...0.24.1)</small>

### Code Refactoring

- Support new pymdownx-highlight options ([a7a2907](https://github.com/mkdocstrings/mkdocstrings/commit/a7a29079aebcd79be84ac38ce275797920e4c75e) by Timothée Mazzucotelli).
- Backup anchors with id and no href, for compatibility with autorefs' Markdown anchors ([b5236b4](https://github.com/mkdocstrings/mkdocstrings/commit/b5236b4333ebde9648c84f6e4b0f4c2b10f3ecd4) by Timothée Mazzucotelli). [PR-#651](https://github.com/mkdocstrings/mkdocstrings/pull/651), [Related-to-mkdocs-autorefs#39](https://github.com/mkdocstrings/autorefs/pull/39), Co-authored-by: Oleh Prypin <oleh@pryp.in>

## [0.24.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.24.0) - 2023-11-14

<small>[Compare with 0.23.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.23.0...0.24.0)</small>

### Features

- Cache downloaded inventories as local file ([ce84dd5](https://github.com/mkdocstrings/mkdocstrings/commit/ce84dd57dc5cd3bf3f4be9623ddaa73e1c1868f0) by Oleh Prypin). [PR #632](https://github.com/mkdocstrings/mkdocstrings/pull/632)

### Bug Fixes

- Make `custom_templates` relative to the config file ([370a61d](https://github.com/mkdocstrings/mkdocstrings/commit/370a61d12b33f3fb61f6bddb3939eb8ff6018620) by Waylan Limberg). [Issue #477](https://github.com/mkdocstrings/mkdocstrings/issues/477), [PR #627](https://github.com/mkdocstrings/mkdocstrings/pull/627)
- Remove duplicated headings for docstrings nested in tabs/admonitions ([e2123a9](https://github.com/mkdocstrings/mkdocstrings/commit/e2123a935edea0abdc1b439e2c2b76e002c76e2b) by Perceval Wajsburt, [f4a94f7](https://github.com/mkdocstrings/mkdocstrings/commit/f4a94f7d8b8eb1ac01d65bb7237f0077e320ddac) by Oleh Prypin). [Issue #609](https://github.com/mkdocstrings/mkdocstrings/issues/609), [PR #610](https://github.com/mkdocstrings/mkdocstrings/pull/610), [PR #613](https://github.com/mkdocstrings/mkdocstrings/pull/613)

### Code Refactoring

- Drop support for MkDocs < 1.4, modernize usages ([b61d4d1](https://github.com/mkdocstrings/mkdocstrings/commit/b61d4d15258c66b14266aa04b456f191f101b2c6) by Oleh Prypin). [PR #629](https://github.com/mkdocstrings/mkdocstrings/pull/629)

## [0.23.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.23.0) - 2023-08-28

<small>[Compare with 0.22.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.22.0...0.23.0)</small>

### Breaking Changes

- Removed `BaseCollector` and `BaseRenderer` classes: they were merged into the `BaseHandler` class.
- Removed the watch feature, as MkDocs now provides it natively.
- Removed support for `selection` and `rendering` keys in YAML blocks: use `options` instead.
- Removed support for loading handlers from the `mkdocstrings.handler` namespace.
  Handlers must now be packaged under the `mkdocstrings_handlers` namespace.

### Features

- Register all anchors for each object in the inventory ([228fb73](https://github.com/mkdocstrings/mkdocstrings/commit/228fb737caca4e20e600053bf59cbfa3e9c73906) by Timothée Mazzucotelli).

### Bug Fixes

- Don't add `codehilite` CSS class to inline code ([7690d41](https://github.com/mkdocstrings/mkdocstrings/commit/7690d41e2871997464367e673023585c4fb05e26) by Timothée Mazzucotelli).
- Support cross-references for API docs rendered in top-level index page ([b194452](https://github.com/mkdocstrings/mkdocstrings/commit/b194452be93aee33b3c28a468762b4d96c501f4f) by Timothée Mazzucotelli).

### Code Refactoring

- Sort inventories before writing them to disk ([9371e9f](https://github.com/mkdocstrings/mkdocstrings/commit/9371e9fc7dd68506b73aa1580a12c5f5cd779aba) by Timothée Mazzucotelli).
- Stop accepting sets as return value of `get_anchors` (only tuples), to preserve order ([2e10374](https://github.com/mkdocstrings/mkdocstrings/commit/2e10374be258e9713b26f73dd06d0c2520ec07a5) by Timothée Mazzucotelli).
- Remove deprecated parts ([0a90a47](https://github.com/mkdocstrings/mkdocstrings/commit/0a90a474c8dcbd95821700d7dab63f03e392c40f) by Timothée Mazzucotelli).
- Use proper parameters in `Inventory.register` method ([433c6e0](https://github.com/mkdocstrings/mkdocstrings/commit/433c6e01aab9333589f755e483f124db0836f143) by Timothée Mazzucotelli).

## [0.22.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.22.0) - 2023-05-25

<small>[Compare with 0.21.2](https://github.com/mkdocstrings/mkdocstrings/compare/0.21.2...0.22.0)</small>

### Features

- Allow extensions to add templates ([cf0af05](https://github.com/mkdocstrings/mkdocstrings/commit/cf0af059eb89240eba0437de417c124389e2f20e) by Timothée Mazzucotelli). [PR #569](https://github.com/mkdocstrings/mkdocstrings/pull/569)

### Code Refactoring

- Report inventory loading errors ([2c05d78](https://github.com/mkdocstrings/mkdocstrings/commit/2c05d7854b87251e26c1a2e1810b85702ff110f3) by Timothée Mazzucotelli). Co-authored-by: Oleh Prypin <oleh@pryp.in>

## [0.21.2](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.21.2) - 2023-04-06

<small>[Compare with 0.21.1](https://github.com/mkdocstrings/mkdocstrings/compare/0.21.1...0.21.2)</small>

### Bug Fixes

- Fix regression with LRU cached method ([85efbd2](https://github.com/mkdocstrings/mkdocstrings/commit/85efbd285d4c8977755bda1c36220b241a9e1502) by Timothée Mazzucotelli). [Issue #549](https://github.com/mkdocstrings/mkdocstrings/issues/549)

## [0.21.1](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.21.1) - 2023-04-05

<small>[Compare with 0.21.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.21.0...0.21.1)</small>

### Bug Fixes

- Fix missing typing-extensions dependency on Python less than 3.10 ([bff760b](https://github.com/mkdocstrings/mkdocstrings/commit/bff760b77c1eedfa770e852aa994a69ff51b0a32) by Timothée Mazzucotelli). [Issue #548](https://github.com/mkdocstrings/mkdocstrings/issues/548)

## [0.21.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.21.0) - 2023-04-05

<small>[Compare with 0.20.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.20.0...0.21.0)</small>

### Features

- Expose the full config to handlers ([15dacf6](https://github.com/mkdocstrings/mkdocstrings/commit/15dacf62f8479a05e9604383155ffa6fade0522d) by David Patterson). [Issue #501](https://github.com/mkdocstrings/mkdocstrings/issues/501), [PR #509](https://github.com/mkdocstrings/mkdocstrings/pull/509)

## [0.20.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.20.0) - 2023-01-19

<small>[Compare with 0.19.1](https://github.com/mkdocstrings/mkdocstrings/compare/0.19.1...0.20.0)</small>

### Features
- Add `enabled` configuration option ([8cf117d](https://github.com/mkdocstrings/mkdocstrings/commit/8cf117daeefb4fc522145cc567b40eb4256c0a94) by StefanBRas). [Issue #478](https://github.com/mkdocstrings/mkdocstrings/issues/478), [PR #504](https://github.com/mkdocstrings/mkdocstrings/pull/504)

### Bug Fixes
- Handle updating Jinja environment of multiple handlers ([a6ea80c](https://github.com/mkdocstrings/mkdocstrings/commit/a6ea80c992f2a200d8cee3c9ff3b651ddd049a3d) by David Patterson). [Related PR #201](https://github.com/mkdocstrings/mkdocstrings/pull/201), [Issue #502](https://github.com/mkdocstrings/mkdocstrings/issues/502), [PR #507](https://github.com/mkdocstrings/mkdocstrings/pull/507)

### Code Refactoring
- Make `_load_inventory` accept lists as arguments ([105ed82](https://github.com/mkdocstrings/mkdocstrings/commit/105ed8210d4665f6b52f2cc04d56df2d35cd3caf) by Sorin Sbarnea). [Needed by PR mkdocstrings/python#49](https://github.com/mkdocstrings/python/issues/49), [PR #511](https://github.com/mkdocstrings/mkdocstrings/pull/511)
- Remove support for MkDocs < 1.2 (we already depended on MkDocs >= 1.2) ([ac963c8](https://github.com/mkdocstrings/mkdocstrings/commit/ac963c88c793e640d2a7a31392aff1fc2d15ba52) by Timothée Mazzucotelli).

## [0.19.1](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.19.1) - 2022-12-13

<small>[Compare with 0.19.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.19.0...0.19.1)</small>

### Bug Fixes
- Fix regular expression for Sphinx inventory parsing ([348bdd5](https://github.com/mkdocstrings/mkdocstrings/commit/348bdd5e930f3cf7a8e27835189794ec940ae1b7) by Luis Michaelis). [Issue #496](https://github.com/mkdocstrings/mkdocstrings/issues/496), [PR #497](https://github.com/mkdocstrings/mkdocstrings/issues/497)

### Code Refactoring
- Small fixes to type annotations ([9214b74](https://github.com/mkdocstrings/mkdocstrings/commit/9214b74367da1f9c808eacc8ceecc4134d5c9d3c) by Oleh Prypin). [PR #470](https://github.com/mkdocstrings/mkdocstrings/issues/470)
- Report usage-based warnings as user-facing messages ([03dd7a6](https://github.com/mkdocstrings/mkdocstrings/commit/03dd7a6e4fefa44889bda9899d9b698bcfd07990) by Oleh Prypin). [PR #464](https://github.com/mkdocstrings/mkdocstrings/issues/464)


## [0.19.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.19.0) - 2022-05-28

<small>[Compare with 0.18.1](https://github.com/mkdocstrings/mkdocstrings/compare/0.18.1...0.19.0)</small>

### Highlights
We decided to deprecate a few things to pave the way towards a more
stable code base, bringing us closer to a v1.

- Selection and rendering options are now combined into a single
  `options` key. Using the old keys will emit a deprecation warning.
- The `BaseCollector` and `BaseRenderer` classes are deprecated in favor
  of `BaseHandler`, which merges their functionality. Using the old
  classes will emit a deprecation warning.

New versions of the Python handler and the legacy Python handler
were also released in coordination with *mkdocstrings* 0.19.
See their respective changelogs:
[python](https://mkdocstrings.github.io/python/changelog/#070-2022-05-28),
[python-legacy](https://mkdocstrings.github.io/python-legacy/changelog/#023-2022-05-28).
Most notably, the Python handler gained the `members` and `filters` options
that prevented many users to switch to it.

*mkdocstrings* stopped depending directly on the legacy Python handler.
It means you now have to explicitely depend on it, directly or through
the extra provided by *mkdocstrings*, if you want to continue using it.

### Packaging / Dependencies
- Stop depending directly on mkdocstrings-python-legacy ([9055d58](https://github.com/mkdocstrings/mkdocstrings/commit/9055d582a6244a45a1af1aeccd8bf3436889a1a5) by Timothée Mazzucotelli). [Issue #376](https://github.com/mkdocstrings/mkdocstrings/issues/376)

### Features
- Pass config file path to handlers ([cccebc4](https://github.com/mkdocstrings/mkdocstrings/commit/cccebc40c0d51c23381d53432d9355fba9a290ae) by Timothée Mazzucotelli). [Issue #311](https://github.com/mkdocstrings/mkdocstrings/issues/311), [PR #425](https://github.com/mkdocstrings/mkdocstrings/issues/425)

### Code Refactoring
- Support options / deprecated options mix-up ([7c71f26](https://github.com/mkdocstrings/mkdocstrings/commit/7c71f2623b667d43c5e9eb8aea881df2c9984a0e) by Timothée Mazzucotelli).
- Deprecate watch feature in favor of MkDocs' built-in one ([c20022e](https://github.com/mkdocstrings/mkdocstrings/commit/c20022e6adfd3a18fd698f50355dfce534b9feb9) by Timothée Mazzucotelli).
- Log relative template paths if possible, instead of absolute ([91f5f83](https://github.com/mkdocstrings/mkdocstrings/commit/91f5f83408c7aab9124cc19fa47c940541d6f5ec) by Timothée Mazzucotelli).
- Deprecate `selection` and `rendering` YAML keys ([3335310](https://github.com/mkdocstrings/mkdocstrings/commit/3335310b985401642fea8322aba503cafa1c50b1) by Timothée Mazzucotelli). [PR #420](https://github.com/mkdocstrings/mkdocstrings/issues/420)
- Deprecate `BaseCollector` and `BaseRenderer` ([eb822cb](https://github.com/mkdocstrings/mkdocstrings/commit/eb822cb11ec065da0b1277299aae4ffeeffadc6f) by Timothée Mazzucotelli). [PR #413](https://github.com/mkdocstrings/mkdocstrings/issues/413)


## [0.18.1](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.18.1) - 2022-03-01

<small>[Compare with 0.18.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.18.0...0.18.1)</small>

### Bug Fixes
- Don't preemptively register identifiers as anchors ([c7ac043](https://github.com/mkdocstrings/mkdocstrings/commit/c7ac04324d005d9cf7d2c1f3b2c39f212275d451) by Timothée Mazzucotelli).


## [0.18.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.18.0) - 2022-02-06

<small>[Compare with 0.17.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.17.0...0.18.0)</small>

### Highlights
- Python 3.6 support is dropped.
- We provide a new, experimental Python handler based on [Griffe](https://github.com/mkdocstrings/griffe).
  This new handler brings automatic cross-references for every annotation in your code,
  including references to third-party libraries' APIs if they provide objects inventories
  and you explicitely [load them](https://mkdocstrings.github.io/usage/#cross-references-to-other-projects-inventories) in `mkdocs.yml`.
  [See migration notes in the documentation](https://mkdocstrings.github.io/handlers/overview/#about-the-python-handlers).
- The "legacy" Python handler now lives in its own repository at https://github.com/mkdocstrings/python-legacy.

### Packaging / Dependencies
- Add Crystal extra, update Python extras versions ([b8222b0](https://github.com/mkdocstrings/mkdocstrings/commit/b8222b0150d4743be857bcbf40f014265095885b) by Timothée Mazzucotelli). [PR #374](https://github.com/mkdocstrings/mkdocstrings/pull/374)
- Update autorefs to actually required version ([fc6c7f6](https://github.com/mkdocstrings/mkdocstrings/commit/fc6c7f652a420ac29cf16cbb99b11a55aa9b38ea) by Timothée Mazzucotelli).
- Drop Python 3.6 support ([7205ac6](https://github.com/mkdocstrings/mkdocstrings/commit/7205ac6cf2861db61c2a5b8bf07d0e6b1a7f49fb) by Timothée Mazzucotelli).

### Features
- Allow unwrapping the `<p>` tag in `convert_markdown` filter ([5351fc8](https://github.com/mkdocstrings/mkdocstrings/commit/5351fc8b417fb20f0681a22f49fcc902579eacdb) by Oleh Prypin). [PR #369](https://github.com/mkdocstrings/mkdocstrings/pull/369)
- Support handlers spanning multiple locations ([f42dfc6](https://github.com/mkdocstrings/mkdocstrings/commit/f42dfc61ce4f9f317c4bd17f568e504ed9764d35) by Timothée Mazzucotelli). [PR #355](https://github.com/mkdocstrings/mkdocstrings/pull/355)

### Code Refactoring
- Prefix logs with the package name only ([6c2b734](https://github.com/mkdocstrings/mkdocstrings/commit/6c2b7348ae40989e4adccc087feae599fcea949d) by Timothée Mazzucotelli). [PR #375](https://github.com/mkdocstrings/mkdocstrings/pull/375)
- Extract the Python handler into its own repository ([74371e4](https://github.com/mkdocstrings/mkdocstrings/commit/74371e49c32059fefd34c7cc7f7b8f085b383237) by Timothée Mazzucotelli). [PR #356](https://github.com/mkdocstrings/mkdocstrings/pull/356)
- Support Jinja2 3.1 ([b377227](https://github.com/mkdocstrings/mkdocstrings/commit/b37722716b1e0ed6393ec71308dfb0f85e142f3b) by Timothée Mazzucotelli). [Issue #360](https://github.com/mkdocstrings/mkdocstrings/issues/360), [PR #361](https://github.com/mkdocstrings/mkdocstrings/pull/361)
- Find templates in new and deprecated namespaces ([d5d5f18](https://github.com/mkdocstrings/mkdocstrings/commit/d5d5f1844dbac3affacc95f2f3eab57a61d2068c) by Timothée Mazzucotelli). [PR #367](https://github.com/mkdocstrings/mkdocstrings/pull/367)
- Support loading handlers from the `mkdocstrings_handlers` namespace ([5c22c6c](https://github.com/mkdocstrings/mkdocstrings/commit/5c22c6ce4e056ac2334e2dfcd47c1f1a7884d352) by Timothée Mazzucotelli). [PR #367](https://github.com/mkdocstrings/mkdocstrings/pull/367)


## [0.17.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.17.0) - 2021-12-27

<small>[Compare with 0.16.2](https://github.com/mkdocstrings/mkdocstrings/compare/0.16.2...0.17.0)</small>

### Features
- Add `show_signature` rendering option ([024ee82](https://github.com/mkdocstrings/mkdocstrings/commit/024ee826bb6f0aa297ba857bc18075d6f4162cad) by Will Da Silva). [Issue #341](https://github.com/mkdocstrings/mkdocstrings/issues/341), [PR #342](https://github.com/mkdocstrings/mkdocstrings/pull/342)
- Support Keyword Args and Yields sections ([1286427](https://github.com/mkdocstrings/mkdocstrings/commit/12864271b7f997af7b421a834919b1e686793905) by Timothée Mazzucotelli). [Issue #205](https://github.com/mkdocstrings/mkdocstrings/issues/205) and [#324](https://github.com/mkdocstrings/mkdocstrings/issues/324), [PR #331](https://github.com/mkdocstrings/mkdocstrings/pull/331)

### Bug Fixes
- Do minimum work when falling back to re-collecting an object to get its anchor ([f6cf570](https://github.com/mkdocstrings/mkdocstrings/commit/f6cf570255df17db1088b6e6cd94bcc823b3b17f) by Timothée Mazzucotelli). [Issue #329](https://github.com/mkdocstrings/mkdocstrings/issues/329), [PR #330](https://github.com/mkdocstrings/mkdocstrings/pull/330)

### Code Refactoring
- Return multiple identifiers from fallback method ([78c498c](https://github.com/mkdocstrings/mkdocstrings/commit/78c498c4a6cfc33cc6ceab9829426bd64e518d44) by Timothée Mazzucotelli). [Issue mkdocstrings/autorefs#11](https://github.com/mkdocstrings/autorefs/issues/11), [PR #350](https://github.com/mkdocstrings/mkdocstrings/pull/350)


## [0.16.2](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.16.2) - 2021-10-04

<small>[Compare with 0.16.1](https://github.com/mkdocstrings/mkdocstrings/compare/0.16.1...0.16.2)</small>

### Dependencies
- Support `pymdown-extensions` v9.x ([0831343](https://github.com/mkdocstrings/mkdocstrings/commit/0831343aa8726ed785b17bba1c8d4adf49b46748) by Ofek Lev and [38b22ec](https://github.com/mkdocstrings/mkdocstrings/commit/38b22ec11cded4689115dafc43e16a1e8e40feda) by Timothée Mazzucotelli).


## [0.16.1](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.16.1) - 2021-09-23

<small>[Compare with 0.16.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.16.0...0.16.1)</small>

### Bug Fixes
- Fix ReadTheDocs "return" template ([598621b](https://github.com/mkdocstrings/mkdocstrings/commit/598621bff29d2aeda0e14f350cda36c1a1f418d5) by Timothée Mazzucotelli).


## [0.16.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.16.0) - 2021-09-20

<small>[Compare with 0.15.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.15.0...0.16.0)</small>

### Features
- Add a rendering option to change the sorting of members ([b1fff8b](https://github.com/mkdocstrings/mkdocstrings/commit/b1fff8b8ef4d6d77417fc43ed8be4b578d6437e4) by Joe Rickerby). [Issue #114](https://github.com/mkdocstrings/mkdocstrings/issues/114), [PR #274](https://github.com/mkdocstrings/mkdocstrings/pull/274)
- Add option to show Python base classes ([436f550](https://github.com/mkdocstrings/mkdocstrings/commit/436f5504ad72ab6d1f5b4303e6b68bc84562c32b) by Brian Koropoff). [Issue #269](https://github.com/mkdocstrings/mkdocstrings/issues/269), [PR #297](https://github.com/mkdocstrings/mkdocstrings/pull/297)
- Support loading external Python inventories in Sphinx format ([a8418cb](https://github.com/mkdocstrings/mkdocstrings/commit/a8418cb4c6193d35cdc72508b118a712cf0334e1) by Oleh Prypin). [PR #287](https://github.com/mkdocstrings/mkdocstrings/pull/287)
- Support loading external inventories and linking to them ([8b675f4](https://github.com/mkdocstrings/mkdocstrings/commit/8b675f4671f8bbfd2f337ed043e3682b0a0ad0f6) by Oleh Prypin). [PR #277](https://github.com/mkdocstrings/mkdocstrings/pull/277)
- Very basic support for MkDocs theme ([974ca90](https://github.com/mkdocstrings/mkdocstrings/commit/974ca9010efca1b8279767faf8efcd2470a8371d) by Oleh Prypin). [PR #272](https://github.com/mkdocstrings/mkdocstrings/pull/272)
- Generate objects inventory ([14ed959](https://github.com/mkdocstrings/mkdocstrings/commit/14ed959860a784a835cd71f911081f2026d66c81) and [bbd85a9](https://github.com/mkdocstrings/mkdocstrings/commit/bbd85a92fa70bddfe10a907a4d63b8daf0810cb2) by Timothée Mazzucotelli). [Issue #251](https://github.com/mkdocstrings/mkdocstrings/issues/251), [PR #253](https://github.com/mkdocstrings/mkdocstrings/pull/253)

### Bug Fixes
- Don't render empty code blocks for missing type annotations ([d2e9e1e](https://github.com/mkdocstrings/mkdocstrings/commit/d2e9e1ef3cf304081b07f763843a9722bf9b117e) by Oleh Prypin).
- Fix custom handler not being used ([6dcf342](https://github.com/mkdocstrings/mkdocstrings/commit/6dcf342fb83b19e385d56d37235f2b23e8c8c767) by Timothée Mazzucotelli). [Issue #259](https://github.com/mkdocstrings/mkdocstrings/issues/259), [PR #263](https://github.com/mkdocstrings/mkdocstrings/pull/263)
- Don't hide `setup_commands` errors ([92418c4](https://github.com/mkdocstrings/mkdocstrings/commit/92418c4b3e80b67d5116efa73931fc113daa60e9) by Gabriel Vîjială). [PR #258](https://github.com/mkdocstrings/mkdocstrings/pull/258)

### Code Refactoring
- Move writing extra files to an earlier stage in the build ([3890ab5](https://github.com/mkdocstrings/mkdocstrings/commit/3890ab597692e56d7ece576c166373b66ff4e615) by Oleh Prypin). [PR #275](https://github.com/mkdocstrings/mkdocstrings/pull/275)


## [0.15.2](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.15.2) - 2021-06-09

<small>[Compare with 0.15.1](https://github.com/mkdocstrings/mkdocstrings/compare/0.15.1...0.15.2)</small>

### Packaging
- MkDocs default schema needs to be obtained differently now ([b3e122b](https://github.com/mkdocstrings/mkdocstrings/commit/b3e122b36d586632738ddedaed7d3df8d5dead44) by Oleh Prypin). [PR #273](https://github.com/mkdocstrings/mkdocstrings/pull/273)
- Compatibility with MkDocs 1.2: livereload isn't guaranteed now ([36e8024](https://github.com/mkdocstrings/mkdocstrings/commit/36e80248d2ab9e61975f6c83ae517115c9410fc1) by Oleh Prypin). [PR #294](https://github.com/mkdocstrings/mkdocstrings/pull/294)


## [0.15.1](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.15.1) - 2021-05-16

<small>[Compare with 0.15.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.15.0...0.15.1)</small>

### Bug Fixes
- Prevent error during parallel installations ([fac2c71](https://github.com/mkdocstrings/mkdocstrings/commit/fac2c711351f7b62bf5308f19cfc612a3944588a) by Timothée Mazzucotelli).

### Packaging
- Support the upcoming major Jinja and MarkupSafe releases ([bb4f9de](https://github.com/mkdocstrings/mkdocstrings/commit/bb4f9de08a77bef85e550d70deb0db13e6aa0c96) by Oleh Prypin). [PR #283](https://github.com/mkdocstrings/mkdocstrings/pull/283)
- Accept a higher version of mkdocs-autorefs ([c8de08e](https://github.com/mkdocstrings/mkdocstrings/commit/c8de08e177f78290d3baaca2716d1ec64c9059b6) by Oleh Prypin). [PR #282](https://github.com/mkdocstrings/mkdocstrings/pull/282)


## [0.15.0](https://github.com/mkdocstrings/mkdocstrings/releases/tag/0.15.0) - 2021-02-28

<small>[Compare with 0.14.0](https://github.com/mkdocstrings/mkdocstrings/compare/0.14.0...0.15.0)</small>

### Breaking Changes

The following items are *possible* breaking changes:

- Cross-linking to arbitrary headings now requires to opt-in to the *autorefs* plugin,
  which is installed as a dependency of *mkdocstrings*.
  See [Cross-references to any Markdown heading](https://mkdocstrings.github.io/usage/#cross-references-to-any-markdown-heading).
- *mkdocstrings* now respects your configured code highlighting method,
  so if you are using the CodeHilite extension, the `.highlight` CSS class in the rendered HTML will become `.codehilite`.
  So make sure to adapt your extra CSS accordingly. Or just switch to using [pymdownx.highlight](https://facelessuser.github.io/pymdown-extensions/extensions/highlight/), it's better supported by *mkdocstrings* anyway.
  See [Syntax highlighting](https://mkdocstrings.github.io/theming/#syntax-highlighting).
- Most of the [CSS rules that *mkdocstrings* used to recommend](https://mkdocstrings.github.io/handlers/python/#recommended-style-material) for manual addition, now become mandatory (auto-injected into the site). This shouldn't *break* any of your styles, but you are welcome to remove the now-redundant lines that you had copied into `extra_css`, [similarly to this diff](https://github.com/mkdocstrings/mkdocstrings/pull/218/files#diff-7889a1924c66ff9318f1d81c4a3b75658d09bebf0db3b2e4023ba3e40294eb73).

### Features
- Nicer-looking error outputs - no tracebacks from mkdocstrings ([6baf720](https://github.com/mkdocstrings/mkdocstrings/commit/6baf720850d359ddb55713553a757fe7b2283e10) by Oleh Prypin). [PR #230](https://github.com/mkdocstrings/mkdocstrings/pull/230)
- Let handlers add CSS to the pages, do so for Python handler ([05c7a3f](https://github.com/mkdocstrings/mkdocstrings/commit/05c7a3fc83b67d3244ea3bfe97dab19aa53f2d38) by Oleh Prypin). [Issue #189](https://github.com/mkdocstrings/mkdocstrings/issues/189), [PR #218](https://github.com/mkdocstrings/mkdocstrings/pull/218)
- Allow linking to an object heading not only by its canonical identifier, but also by its possible aliases ([4789950](https://github.com/mkdocstrings/mkdocstrings/commit/4789950ff43c354d47afbed5c89d5abb917ffee6) by Oleh Prypin). [PR #217](https://github.com/mkdocstrings/mkdocstrings/pull/217)

### Bug Fixes
- Propagate the CSS class to inline highlighting as well ([c7d80e6](https://github.com/mkdocstrings/mkdocstrings/commit/c7d80e63a042913b7511c38a788967796dd10997) by Oleh Prypin). [PR #245](https://github.com/mkdocstrings/mkdocstrings/pull/245)
- Don't double-escape characters in highlighted headings ([6357144](https://github.com/mkdocstrings/mkdocstrings/commit/6357144b100be6a2e7e6140e035c289c225cec22) by Oleh Prypin). [Issue #228](https://github.com/mkdocstrings/mkdocstrings/issues/228), [PR #241](https://github.com/mkdocstrings/mkdocstrings/pull/241)

### Code Refactoring
- Use the autorefs plugin from its new external location ([e2d74ef](https://github.com/mkdocstrings/mkdocstrings/commit/e2d74efb0d59f9a1aa45e42525ceb1d4b7638426) by Oleh Prypin). [PR #235](https://github.com/mkdocstrings/mkdocstrings/pull/235)
- Split out Markdown extensions from `handlers` to `handlers.rendering` ([7533852](https://github.com/mkdocstrings/mkdocstrings/commit/7533852e3ac0a378b70a380cef1100421b7d5763) by Oleh Prypin). [PR #233](https://github.com/mkdocstrings/mkdocstrings/pull/233)
- Theme-agnostic code highlighting, respecting configs ([f9ea009](https://github.com/mkdocstrings/mkdocstrings/commit/f9ea00979545e39983ba377f1930d73ae94165ea) by Oleh Prypin). [PR #202](https://github.com/mkdocstrings/mkdocstrings/pull/202)
- Split out autorefs plugin, make it optional ([fc67656](https://github.com/mkdocstrings/mkdocstrings/commit/fc676564f9b11269b3e0b0482703ac924069a3fa) by Oleh Prypin). [PR #220](https://github.com/mkdocstrings/mkdocstrings/pull/220)
- Remove the extra wrapper div from the final doc ([7fe438c](https://github.com/mkdocstrings/mkdocstrings/commit/7fe438c4040a2124b00c39e582ef4c38be7c55c9) by Oleh Prypin). [PR #209](https://github.com/mkdocstrings/mkdocstrings/pull/209)
- Don't re-parse the whole subdoc, expose only headings ([15f84f9](https://github.com/mkdocstrings/mkdocstrings/commit/15f84f981982c8e2b15498f5c869ac207f3ce5d7) by Oleh Prypin). [PR #209](https://github.com/mkdocstrings/mkdocstrings/pull/209)
- Actually exclude hidden headings from the doc ([0fdb082](https://github.com/mkdocstrings/mkdocstrings/commit/0fdb0821867eb0e14a972a603c22301aafecf4f4) by Oleh Prypin). [PR #209](https://github.com/mkdocstrings/mkdocstrings/pull/209)


## [0.14.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.14.0) - 2021-01-06

<small>[Compare with 0.13.6](https://github.com/pawamoy/mkdocstrings/compare/0.13.6...0.14.0)</small>

Special thanks to Oleh [@oprypin](https://github.com/oprypin) Prypin who did an amazing job (this is a euphemism)
at improving *mkdocstrings*, fixing hard-to-fix bugs with clever solutions, implementing great new features
and refactoring the code for better performance and readability! Thanks Oleh!

### Bug Fixes
- Fix double code tags ([e84d401](https://github.com/pawamoy/mkdocstrings/commit/e84d401c6dcb9aecb8cc1a58d3a0f339e1c3e78f) by Timothée Mazzucotelli).
- Don't mutate the original Markdown config for permalinks ([8f6b163](https://github.com/pawamoy/mkdocstrings/commit/8f6b163b50551da22f65e9b736e042562f77f2d7) by Oleh Prypin).
- Preserve text immediately before an autodoc ([07466fa](https://github.com/pawamoy/mkdocstrings/commit/07466fafb54963a4e35e69007b6291a0382aaeb4) by Oleh Prypin). [PR #207](https://github.com/pawamoy/mkdocstrings/pull/207)
- Remove `href` attributes from headings in templates ([d5602ff](https://github.com/pawamoy/mkdocstrings/commit/d5602ff3bb1a75ac1c8c457e972271b6c66eb8dd) by Oleh Prypin). [PR #204](https://github.com/pawamoy/mkdocstrings/pull/204)
- Don't let `toc` extension append its permalink twice ([a154f5c](https://github.com/pawamoy/mkdocstrings/commit/a154f5c4c6ef9abd221e1f89e44847ae2cf25436) by Oleh Prypin). [PR #203](https://github.com/pawamoy/mkdocstrings/pull/203)
- Fix undefined entity for `&para;` ([2c29211](https://github.com/pawamoy/mkdocstrings/commit/2c29211002d515db40e5bdabf6cbf32ec8633a05) by Timothée Mazzucotelli).
- Make ids of Markdown sub-documents prefixed with the parent item id ([d493d33](https://github.com/pawamoy/mkdocstrings/commit/d493d33b3827d93e84a7b2e39f0a10dfcb782402) by Oleh Prypin). [Issue #186](https://github.com/pawamoy/mkdocstrings/issues/186) and [#193](https://github.com/pawamoy/mkdocstrings/issues/193), [PR #199](https://github.com/pawamoy/mkdocstrings/pull/199)
- More lenient regex for data-mkdocstrings-identifier ([dcfec8e](https://github.com/pawamoy/mkdocstrings/commit/dcfec8edfdff050debc5856dfc213d3119a84792) by Oleh Prypin).
- Shift Markdown headings according to the current `heading_level` ([13f41ae](https://github.com/pawamoy/mkdocstrings/commit/13f41aec5a95c82c1229baa4ac3caf4abb2add51) by Oleh Prypin). [Issue #192](https://github.com/pawamoy/mkdocstrings/issues/192), [PR #195](https://github.com/pawamoy/mkdocstrings/pull/195)
- Fix footnotes appearing in all following objects ([af24bc2](https://github.com/pawamoy/mkdocstrings/commit/af24bc246a6938ebcae7cf6ff677b194cf1af95c) by Oleh Prypin). [Issue #186](https://github.com/pawamoy/mkdocstrings/issues/186), [PR #195](https://github.com/pawamoy/mkdocstrings/pull/195)
- Fix cross-references from the root index page ([9c9f2a0](https://github.com/pawamoy/mkdocstrings/commit/9c9f2a04af94e0d88f57fd76249f7985166a9b88) by Oleh Prypin). [Issue #184](https://github.com/pawamoy/mkdocstrings/issues/184), [PR #185](https://github.com/pawamoy/mkdocstrings/pull/185)
- Fix incorrect argument name passed to Markdown ([10ce502](https://github.com/pawamoy/mkdocstrings/commit/10ce502d5fd58f1e5a4e14308ffad1bc3d7116ee) by Timothée Mazzucotelli).
- Fix error when a digit immediately follows a code tag ([9b92341](https://github.com/pawamoy/mkdocstrings/commit/9b9234160edc54b53c81a618b12095e7dd829059) by Oleh Prypin). [Issue #169](https://github.com/pawamoy/mkdocstrings/issues/169), [PR #175](https://github.com/pawamoy/mkdocstrings/pull/175)
- Detecting paths relative to template directory in logging ([a50046b](https://github.com/pawamoy/mkdocstrings/commit/a50046b5d58d62df4ba13f4c197e80edd1995eb9) by Oleh Prypin). [Issue #166](https://github.com/pawamoy/mkdocstrings/issues/166)

### Code Refactoring
- BlockProcessor already receives strings, use them as such ([bcf7da9](https://github.com/pawamoy/mkdocstrings/commit/bcf7da911a310a63351c5082e84bb763d90d5b3b) by Oleh Prypin).
- Remove some unused code ([8504084](https://github.com/pawamoy/mkdocstrings/commit/850408421cc027be8374673cc74c71fff26f3833) by Oleh Prypin). [PR #206](https://github.com/pawamoy/mkdocstrings/pull/206)
- Improve XML parsing error handling ([ad86410](https://github.com/pawamoy/mkdocstrings/commit/ad864100b644ab1ee8daaa0d3923bc87dee1c5ca) by Timothée Mazzucotelli).
- Explicitly use MarkupSafe ([6b9ebe7](https://github.com/pawamoy/mkdocstrings/commit/6b9ebe7d510e82971acef89e9e946af3c0cc96d3) by Oleh Prypin).
- Split out the handler cache, expose it through the plugin ([6453026](https://github.com/pawamoy/mkdocstrings/commit/6453026fac287387090a67cce70c078377d107dd) by Oleh Prypin). [Issue #179](https://github.com/pawamoy/mkdocstrings/issues/179), [PR #191](https://github.com/pawamoy/mkdocstrings/pull/191)
- Use ChainMap instead of copying dicts ([c634d2c](https://github.com/pawamoy/mkdocstrings/commit/c634d2ce6377de26caa553048bb28ef1e672f7aa) by Oleh Prypin). [PR #171](https://github.com/pawamoy/mkdocstrings/pull/171)
- Rename logging to loggers to avoid confusion ([7a119cc](https://github.com/pawamoy/mkdocstrings/commit/7a119ccf27cf77cf2cbd114e7fad0a9e4e97bbd8) by Timothée Mazzucotelli).
- Simplify logging ([409f93e](https://github.com/pawamoy/mkdocstrings/commit/409f93ed26d7d8292a8bc7a6c32cb270b3769409) by Timothée Mazzucotelli).

### Features
- Allow specifying `heading_level` as a Markdown heading ([10efc28](https://github.com/pawamoy/mkdocstrings/commit/10efc281e04b2a430cec53e49208ccc09e591667) by Oleh Prypin). [PR #170](https://github.com/pawamoy/mkdocstrings/pull/170)
- Allow any characters in identifiers ([7ede68a](https://github.com/pawamoy/mkdocstrings/commit/7ede68a0917b494eda2198931a8ad1c97fc8fce4) by Oleh Prypin). [PR #174](https://github.com/pawamoy/mkdocstrings/pull/174)
- Allow namespace packages for handlers ([39b0465](https://github.com/pawamoy/mkdocstrings/commit/39b046548f57dc59993241b24d2cf12fb5e488eb) by Timothée Mazzucotelli).
- Add template debugging/logging ([33b32c1](https://github.com/pawamoy/mkdocstrings/commit/33b32c1410bf6e8432768865c8aa86b8e091ab59) by Timothée Mazzucotelli).
- Add initial support for the ReadTheDocs theme ([1028115](https://github.com/pawamoy/mkdocstrings/commit/1028115682ed0806d6570c749af0e382c67d6120) by Timothée Mazzucotelli). [Issue #107](https://github.com/pawamoy/mkdocstrings/issues/107), [PR #159](https://github.com/pawamoy/mkdocstrings/pull/159)
- Add option to show type annotations in signatures ([f94ce9b](https://github.com/pawamoy/mkdocstrings/commit/f94ce9bdb2afc2c41c21a53636980ca077b757ce) by Timothée Mazzucotelli). [Issue #106](https://github.com/pawamoy/mkdocstrings/issues/106)

### Packaging
- Accept verions of `pytkdocs` up to 0.10.x (see [changelog](https://pawamoy.github.io/pytkdocs/changelog/#0100-2020-12-06)).

### Performance Improvements
- Call `update_env` only once per `Markdown` instance ([b198c74](https://github.com/pawamoy/mkdocstrings/commit/b198c74338dc3b54b999eadeef9946d69277ad77) by Oleh Prypin). [PR #201](https://github.com/pawamoy/mkdocstrings/pull/201)
- Disable Jinja's `auto_reload` to reduce disk reads ([3b28c58](https://github.com/pawamoy/mkdocstrings/commit/3b28c58c77642071419d4a98e007d5a854b7984f) by Oleh Prypin). [PR #200](https://github.com/pawamoy/mkdocstrings/pull/200)
- Rework autorefs replacement to not re-parse the final HTML ([22a9e4b](https://github.com/pawamoy/mkdocstrings/commit/22a9e4bf1b73f9b9b1a7c4876f0c677f919bc4d7) by Oleh Prypin). [Issue #187](https://github.com/pawamoy/mkdocstrings/issues/187), [PR #188](https://github.com/pawamoy/mkdocstrings/pull/188)


## [0.13.6](https://github.com/pawamoy/mkdocstrings/releases/tag/0.13.6) - 2020-09-28

<small>[Compare with 0.13.5](https://github.com/pawamoy/mkdocstrings/compare/0.13.5...0.13.6)</small>

### Bug Fixes
- Fix rendering when clicking on hidden toc entries ([2af4d31](https://github.com/pawamoy/mkdocstrings/commit/2af4d310adefec614235a2c1d04d5ff56bf9c220) by Timothée Mazzucotelli). Issue [#60](https://github.com/pawamoy/mkdocstrings/issues/60).


## [0.13.5](https://github.com/pawamoy/mkdocstrings/releases/tag/0.13.5) - 2020-09-28

<small>[Compare with 0.13.4](https://github.com/pawamoy/mkdocstrings/compare/0.13.4...0.13.5)</small>

## Packaging
- Accept `pytkdocs` version up to 0.9.x ([changelog](https://pawamoy.github.io/pytkdocs/changelog/#090-2020-09-28)).


## [0.13.4](https://github.com/pawamoy/mkdocstrings/releases/tag/0.13.4) - 2020-09-25

<small>[Compare with 0.13.3](https://github.com/pawamoy/mkdocstrings/compare/0.13.3...0.13.4)</small>

### Bug Fixes
- Bring back arbitrary `**config` to Python handler ([fca7d4c](https://github.com/pawamoy/mkdocstrings/commit/fca7d4c75ffd7a84eaeccd27facd5575604dbfab) by Florimond Manca). Issue [#154](https://github.com/pawamoy/mkdocstrings/issues/154), PR [#155](https://github.com/pawamoy/mkdocstrings/pull/155)


## [0.13.3](https://github.com/pawamoy/mkdocstrings/releases/tag/0.13.3) - 2020-09-25

<small>[Compare with 0.13.2](https://github.com/pawamoy/mkdocstrings/compare/0.13.2...0.13.3)</small>

### Packaging
- Accept `pytkdocs` version up to 0.8.x ([changelog](https://pawamoy.github.io/pytkdocs/changelog/#080-2020-09-25)).


## [0.13.2](https://github.com/pawamoy/mkdocstrings/releases/tag/0.13.2) - 2020-09-08

<small>[Compare with 0.13.1](https://github.com/pawamoy/mkdocstrings/compare/0.13.1...0.13.2)</small>

### Bug Fixes
- Fix relative URLs when `use_directory_urls` is false ([421d189](https://github.com/pawamoy/mkdocstrings/commit/421d189fff9ea2608e40d85e0a93e30334782b90) by Timothée Mazzucotelli). References: [#149](https://github.com/pawamoy/mkdocstrings/issues/149)


## [0.13.1](https://github.com/pawamoy/mkdocstrings/releases/tag/0.13.1) - 2020-09-03

<small>[Compare with 0.13.0](https://github.com/pawamoy/mkdocstrings/compare/0.13.0...0.13.1)</small>

### Bug Fixes
- Use relative links for cross-references ([9c77f1f](https://github.com/pawamoy/mkdocstrings/commit/9c77f1f461fa87842ae39945f9521ee85b1e413b) by Timothée Mazzucotelli). References: [#144](https://github.com/pawamoy/mkdocstrings/issues/144), [#147](https://github.com/pawamoy/mkdocstrings/issues/147)


## [0.13.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.13.0) - 2020-08-21

<small>[Compare with 0.12.2](https://github.com/pawamoy/mkdocstrings/compare/0.12.2...0.13.0)</small>

### Bug Fixes
- Accept dashes in module names ([fcf79d0](https://github.com/pawamoy/mkdocstrings/commit/fcf79d0024ec46c3862c94202864e054c04a6d0b) by Timothée Mazzucotelli). References: [#140](https://github.com/pawamoy/mkdocstrings/issues/140)

### Features
- Add option to show full path of direct members only ([d1b9401](https://github.com/pawamoy/mkdocstrings/commit/d1b9401afecb20d3123eec7334605cb15bf9d877) by Aaron Dunmore). References: [#134](https://github.com/pawamoy/mkdocstrings/issues/134), [#136](https://github.com/pawamoy/mkdocstrings/issues/136)

### Packaging
- Accept `pymdown-extensions` versions up to 0.8.x ([see release notes](https://facelessuser.github.io/pymdown-extensions/about/releases/8.0/#8.0)) ([178d48d](https://github.com/pawamoy/mkdocstrings/commit/178d48da7a62daf285dfc5f6ff230e8bce82ed53) by Hugo van Kemenade). PR [#146](https://github.com/pawamoy/mkdocstrings/issue/146)


## [0.12.2](https://github.com/pawamoy/mkdocstrings/releases/tag/0.12.2) - 2020-07-24

<small>[Compare with 0.12.1](https://github.com/pawamoy/mkdocstrings/compare/0.12.1...0.12.2)</small>

### Packaging
- Accept `pytkdocs` version up to 0.7.x ([changelog](https://pawamoy.github.io/pytkdocs/changelog/#070-2020-07-24)).


## [0.12.1](https://github.com/pawamoy/mkdocstrings/releases/tag/0.12.1) - 2020-07-07

<small>[Compare with 0.12.0](https://github.com/pawamoy/mkdocstrings/compare/0.12.0...0.12.1)</small>

### Bug Fixes
- Fix HTML-escaped sequence parsing as XML ([db297f1](https://github.com/pawamoy/mkdocstrings/commit/db297f19013fc402eeff1f2827057a959e481c66) by Timothée Mazzucotelli).
- Allow running mkdocs from non-default interpreter ([283dd7b](https://github.com/pawamoy/mkdocstrings/commit/283dd7b83eeba675a16d96d2e829851c1273a625) by Jared Khan).


## [0.12.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.12.0) - 2020-06-14

<small>[Compare with 0.11.4](https://github.com/pawamoy/mkdocstrings/compare/0.11.4...0.12.0)</small>

### Features
- Support attributes section in Google-style docstrings ([8300253](https://github.com/pawamoy/mkdocstrings/commit/83002532b2294ea33dcec4f2672a5a6d0f64def1) by Timothée Mazzucotelli). References: [#88](https://github.com/pawamoy/mkdocstrings/issues/88)
- Support examples section in Google-style docstrings ([650c754](https://github.com/pawamoy/mkdocstrings/commit/650c754afdd5d4fb96b1e2529f378d025a2e7daf) by Iago González). References: [#112](https://github.com/pawamoy/mkdocstrings/issues/112)

### Packaging
- Accept `pytkdocs` version up to 0.6.x ([changelog](https://pawamoy.github.io/pytkdocs/changelog/#060-2020-06-14)).

## [0.11.4](https://github.com/pawamoy/mkdocstrings/releases/tag/0.11.4) - 2020-06-08

<small>[Compare with 0.11.3](https://github.com/pawamoy/mkdocstrings/compare/0.11.3...0.11.4)</small>

### Packaging
- Accept `pytkdocs` version up to 0.5.x ([changelog](https://pawamoy.github.io/pytkdocs/changelog/#050-2020-06-08)).
  If it breaks your docs, please [open issues on `pytkdocs`' bug-tracker](https://github.com/pawamoy/pytkdocs/issues),
  or pin `pytkdocs` version to while waiting for bug fixes <0.5.0 :clown:.


## [0.11.3](https://github.com/pawamoy/mkdocstrings/releases/tag/0.11.3) - 2020-06-07

<small>[Compare with 0.11.2](https://github.com/pawamoy/mkdocstrings/compare/0.11.2...0.11.3)</small>

### Bug Fixes
- Support custom theme directory configuration ([1243cf6](https://github.com/pawamoy/mkdocstrings/commit/1243cf673aaf371e5cbf42a3e0d1aa80482398a3) by Abhishek Thakur). References: [#120](https://github.com/pawamoy/mkdocstrings/issues/120), [#121](https://github.com/pawamoy/mkdocstrings/issues/121)


## [0.11.2](https://github.com/pawamoy/mkdocstrings/releases/tag/0.11.2) - 2020-05-20

<small>[Compare with 0.11.1](https://github.com/pawamoy/mkdocstrings/compare/0.11.1...0.11.2)</small>

### Packaging
- Increase `pytkdocs` version range to accept 0.4.0
  ([changelog](https://pawamoy.github.io/pytkdocs/changelog/#040-2020-05-17)).


## [0.11.1](https://github.com/pawamoy/mkdocstrings/releases/tag/0.11.1) - 2020-05-14

<small>[Compare with 0.11.0](https://github.com/pawamoy/mkdocstrings/compare/0.11.0...0.11.1)</small>

### Bug Fixes
- Fix integration with mkdocs logging *une bonne fois pour toute* ([3293cbf](https://github.com/pawamoy/mkdocstrings/commit/3293cbf161f05d36de6c1d50b5de9742bf99066e) by Timothée Mazzucotelli).
- Discard setup commands stdout ([ea44cea](https://github.com/pawamoy/mkdocstrings/commit/ea44cea33159ed3a6b0b34b4cd52a17a40bd6460) by Timothée Mazzucotelli). References: [#91](https://github.com/pawamoy/mkdocstrings/issues/91)
- Use the proper python executable to start subprocesses ([9fe3b39](https://github.com/pawamoy/mkdocstrings/commit/9fe3b3915bd8f15011f8f3632a227d1eb56603fd) by Reece Dunham). References: [#91](https://github.com/pawamoy/mkdocstrings/issues/91), [#103](https://github.com/pawamoy/mkdocstrings/issues/103)


## [0.11.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.11.0) - 2020-04-23

<small>[Compare with 0.10.3](https://github.com/pawamoy/mkdocstrings/compare/0.10.3...0.11.0)</small>

### Bug Fixes
- Properly raise on errors (respect strict mode) ([2097208](https://github.com/pawamoy/mkdocstrings/commit/20972082a94b64bec02c77d6a80384d8042f60ea) by Timothée Mazzucotelli). Related issues/PRs: [#86](https://github.com/pawamoy/mkdocstrings/issues/86)
- Hook properly to MkDocs logging ([b23daed](https://github.com/pawamoy/mkdocstrings/commit/b23daed3743bbd2d3f024df34582a317c51a1af0) by Timothée Mazzucotelli). Related issues/PRs: [#86](https://github.com/pawamoy/mkdocstrings/issues/86)

### Features
- Add `setup_commands` option to python handler ([599f8e5](https://github.com/pawamoy/mkdocstrings/commit/599f8e528f55093b0011b732da959b747c1e02c0) by Ross Mechanic). Related issues/PRs: [#89](https://github.com/pawamoy/mkdocstrings/issues/89), [#90](https://github.com/pawamoy/mkdocstrings/issues/90)
- Add option to allow overriding templates ([7360021](https://github.com/pawamoy/mkdocstrings/commit/7360021ab4753706d0f6209ed960050f5d424ad8) by Mikaël Capelle). Related issues/PRs: [#59](https://github.com/pawamoy/mkdocstrings/issues/59), [#82](https://github.com/pawamoy/mkdocstrings/issues/82)


## [0.10.3](https://github.com/pawamoy/mkdocstrings/releases/tag/0.10.3) - 2020-04-10

<small>[Compare with 0.10.2](https://github.com/pawamoy/mkdocstrings/compare/0.10.2...0.10.3)</small>

### Bug Fixes
- Handle `site_url` not being defined ([9fb4a9b](https://github.com/pawamoy/mkdocstrings/commit/9fb4a9bbebe2457b389921ba1ee3e1f924c5691b) by Timothée Mazzucotelli). Related issues/PRs: [#77](https://github.com/pawamoy/mkdocstrings/issues/77)

### Packaging
This version increases the accepted range of versions for the `pytkdocs` dependency to `>=0.2.0, <0.4.0`.
The `pytkdocs` project just released [version 0.3.0](https://pawamoy.github.io/pytkdocs/changelog/#030-2020-04-10)
which:

- adds support for complex markup in docstrings sections items descriptions
- adds support for different indentations in docstrings sections (tabulations or less/more than 4 spaces)
- fixes docstring parsing for arguments whose names start with `*`, like `*args` and `**kwargs`


## [0.10.2](https://github.com/pawamoy/mkdocstrings/releases/tag/0.10.2) - 2020-04-07

<small>[Compare with 0.10.1](https://github.com/pawamoy/mkdocstrings/compare/0.10.1...0.10.2)</small>

### Packaging
This version increases the accepted range of versions for the `pymdown-extensions` dependency,
as well as for the `mkdocs-material` development dependency. Indeed, both these projects recently
released major versions 7 and 5 respectively. Users who wish to use these new versions will be able to.
See issue [#74](https://github.com/pawamoy/mkdocstrings/issues/74).

## [0.10.1](https://github.com/pawamoy/mkdocstrings/releases/tag/0.10.1) - 2020-04-03

<small>[Compare with 0.10.0](https://github.com/pawamoy/mkdocstrings/compare/0.10.0...0.10.1)</small>

### Bug Fixes
- Fix jinja2 error for jinja2 < 2.11 ([387f970](https://github.com/pawamoy/mkdocstrings/commit/387f97088ad2b7b25389ae6cf303bae071e90e6c) by Timothée Mazzucotelli). Related issues/PRs: [#67](https://github.com/pawamoy/mkdocstrings/issues/67), [#72](https://github.com/pawamoy/mkdocstrings/issues/72)
- Fix missing dependency pymdown-extensions ([648b99d](https://github.com/pawamoy/mkdocstrings/commit/648b99dab9d1af87db474ce7683de50c9bf8996d) by Timothée Mazzucotelli). Related issues/PRs: [#66](https://github.com/pawamoy/mkdocstrings/issues/66)
- Fix heading level of hidden toc entries ([475cc62](https://github.com/pawamoy/mkdocstrings/commit/475cc62b1cf4342b82ca8685166306441e4b83c4) by Timothée Mazzucotelli). Related issues/PRs: [#65](https://github.com/pawamoy/mkdocstrings/issues/65)
- Fix rendering signatures containing keyword_only ([c6c5add](https://github.com/pawamoy/mkdocstrings/commit/c6c5addd8be65beaf7055c9d0f512e0de8b3eba4) by Timothée Mazzucotelli). Related issues/PRs: [#68](https://github.com/pawamoy/mkdocstrings/issues/68)


## [0.10.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.10.0) - 2020-03-27

<small>[Compare with 0.9.1](https://github.com/pawamoy/mkdocstrings/compare/0.9.1...0.10.0)</small>

### Features
- Prepare for new `pytkdocs` version ([336421a](https://github.com/pawamoy/mkdocstrings/commit/336421af95d752671276c2e88c5c173bff4093cc)).
  Add options `filters` and `members` to the Python collector to reflect the new `pytkdocs` options.
  See [the default configuration of the Python collector](https://pawamoy.github.io/mkdocstrings/reference/handlers/python/#mkdocstrings.handlers.python.PythonCollector.DEFAULT_CONFIG).


## [0.9.1](https://github.com/pawamoy/mkdocstrings/releases/tag/0.9.1) - 2020-03-21

<small>[Compare with 0.9.0](https://github.com/pawamoy/mkdocstrings/compare/0.9.0...0.9.1)</small>

### Bug fixes
- Fix cross-references when deploying to GitHub pages ([36f804b](https://github.com/pawamoy/mkdocstrings/commit/36f804beab01531c0331ed89d21f3e5e15bd8585)).


## [0.9.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.9.0) - 2020-03-21

<small>[Compare with 0.8.0](https://github.com/pawamoy/mkdocstrings/compare/0.8.0...0.9.0)</small>

This version is a big refactor. We will just list the new features without pointing to particular commits.
The documentation rendering looks slightly different, and should be better than before.
No identified breaking changes for end-users.

### Features
- **Language agnostic:** we moved the code responsible for loading Python documentation into a new project,
  [`pytkdocs`](https://github.com/pawamoy/pytkdocs), and implemented a "handlers" logic, effectively allowing to
  support any given language. Waiting for your handlers contributions :wink:!
- **Multiple themes support:** handlers can offer templates for multiple `mkdocs` themes.
- **Better cross-references:** cross-references now not only work between documented objects (between all languages,
  given the objects' identifiers are unique), but also for every heading of your Markdown pages.
- **Configuration options:** the rendering of Python documentation can now be configured,
  (globally and locally thanks to the handlers system),
  [check the docs!](https://pawamoy.github.io/mkdocstrings/reference/handlers/python/#mkdocstrings.handlers.python.PythonRenderer.DEFAULT_CONFIG)
  Also see the [recommended CSS](https://pawamoy.github.io/mkdocstrings/handlers/python/#recommended-style).
- **Proper logging messages:** `mkdocstrings` now logs debug, warning and error messages, useful when troubleshooting.

### Bug fixes
- Various fixes and better error handling.


## [0.8.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.8.0) - 2020-03-04

<small>[Compare with 0.7.2](https://github.com/pawamoy/mkdocstrings/compare/0.7.2...0.8.0)</small>

### Breaking Changes
- Be compatible with Mkdocs >= 1.1 ([5a974a4](https://github.com/pawamoy/mkdocstrings/commit/5a974a4eb810904d6836e216d8539affc8acaa6f)).
  This is a breaking change as we're not compatible with versions of Mkdocs below 1.1 anymore.
  If you cannot upgrade Mkdocs to 1.1, pin mkdocstrings' version to 0.7.2.

## [0.7.2](https://github.com/pawamoy/mkdocstrings/releases/tag/0.7.2) - 2020-03-04

<small>[Compare with 0.7.1](https://github.com/pawamoy/mkdocstrings/compare/0.7.1...0.7.2)</small>

### Bug Fixes
- Catch `OSError` when trying to get source lines ([8e8d604](https://github.com/pawamoy/mkdocstrings/commit/8e8d604ba95363c140841c84535d2350d7ebbfe3)).
- Do not render signature empty sentinel ([16dfd73](https://github.com/pawamoy/mkdocstrings/commit/16dfd73cf30d01314dba756d3f10308b99c87dcc)).
- Fix for nested classes and their attributes ([7fef903](https://github.com/pawamoy/mkdocstrings/commit/7fef9037c5299d6106347b0db29f85a644f85c16)).
- Fix `relative_file_path` method ([52715ad](https://github.com/pawamoy/mkdocstrings/commit/52715adc59fe2e26a9e91df88bac8b8b32d4635e)).
- Wrap file path in backticks to escape it ([2525f39](https://github.com/pawamoy/mkdocstrings/commit/2525f39ad8c181679fa33db8e6dfaa28eb39c289)).

## [0.7.1](https://github.com/pawamoy/mkdocstrings/releases/tag/0.7.1) - 2020-02-18

<small>[Compare with 0.7.0](https://github.com/pawamoy/mkdocstrings/compare/0.7.0...0.7.1)</small>

### Bug Fixes
- Replace literal slash with os.sep for Windows compatibility ([70f9af5](https://github.com/pawamoy/mkdocstrings/commit/70f9af5e33cda694cda33870c84a770c853d84b5)).


## [0.7.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.7.0) - 2020-01-13

<small>[Compare with 0.6.1](https://github.com/pawamoy/mkdocstrings/compare/0.6.1...0.7.0)</small>

### Bug Fixes
- Don't mark args or kwargs as required ([4049d6f](https://github.com/pawamoy/mkdocstrings/commit/4049d6f27c332b05db06bcfe6cc564f3c1c0f013)).
- Filter submodules ([7b11095](https://github.com/pawamoy/mkdocstrings/commit/7b110959529c5fc0275fb98c6d97e7c71e205900)).

### Code Refactoring
- Don't guess lang in generated docs ([db4f60a](https://github.com/pawamoy/mkdocstrings/commit/db4f60a13dd0d191d7515683d7d42ae374b39fae)).
- Render at HTML step with custom markdown converter ([9b5a3e1](https://github.com/pawamoy/mkdocstrings/commit/9b5a3e126cd584893a8d0858ca9b67b8251e88f1)).

### Features
- Change forward ref to ref, fix optional unions ([2f0bfaa](https://github.com/pawamoy/mkdocstrings/commit/2f0bfaabf367bfa513c20fb1230409306e43add2)).
- Discover package submodules ([231062a](https://github.com/pawamoy/mkdocstrings/commit/231062a3a107abc02134f102a06693969cf603ad)).
- Implement watched source code (hacks) ([4a67953](https://github.com/pawamoy/mkdocstrings/commit/4a67953c0af9da363d52ba058b3c51cf4cbfaabe)).


## [0.6.1](https://github.com/pawamoy/mkdocstrings/releases/tag/0.6.1) - 2020-01-02

<small>[Compare with 0.6.0](https://github.com/pawamoy/mkdocstrings/compare/0.6.0...0.6.1)</small>

### Bug Fixes
- Break docstring discarding loop if found ([5a17fec](https://github.com/pawamoy/mkdocstrings/commit/5a17fec5beed2003d19ccdcb359b46b79bfcf469)).
- Fix discarding docstring ([143f7cb](https://github.com/pawamoy/mkdocstrings/commit/143f7cb00f02a7d3179cc5606ed7903566250227)).
- Fix getting annotation from nodes ([ecde72b](https://github.com/pawamoy/mkdocstrings/commit/ecde72bb22ccedb36aa847dd50504c63ad04498c)).
- Fix various things ([affbf06](https://github.com/pawamoy/mkdocstrings/commit/affbf064d457d4b626e8f67d38e94d7919bc2df2)).

### Code Refactoring
- Break as soon as we find the same attr in a parent class while trying to discard the docstring ([65d7908](https://github.com/pawamoy/mkdocstrings/commit/65d7908f489ec465b2803ea8f55c70d0f9d7586b)).
- Split Docstring.parse method to improve readability ([2226e2d](https://github.com/pawamoy/mkdocstrings/commit/2226e2d55a6b9bbdd5a56183f1a9ba3c5f01b5ac)).


## [0.6.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.6.0) - 2019-12-28

<small>[Compare with 0.5.0](https://github.com/pawamoy/mkdocstrings/compare/0.5.0...0.6.0)</small>

### Bug Fixes
- Fix GenericMeta import error on Python 3.7+ ([febf2b9](https://github.com/pawamoy/mkdocstrings/commit/febf2b9749d97cce80f5d20339372842fdffc908)).

### Code Refactoring
- More classes. Still ugly code though :'( ([f41c119](https://github.com/pawamoy/mkdocstrings/commit/f41c11988d8d849a0310cca511c2d93a74cab86f)).
- Split into more modules ([f1872a4](https://github.com/pawamoy/mkdocstrings/commit/f1872a4c8d41a0b9603b7f344de3186110a4e1bd)).
- Use Object subclasses ([40dd106](https://github.com/pawamoy/mkdocstrings/commit/40dd1062188e6ad6ef6fbc12ddead2132fe6af1e)).


## [0.5.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.5.0) - 2019-12-22

<small>[Compare with 0.4.0](https://github.com/pawamoy/mkdocstrings/compare/0.4.0...0.5.0)</small>

### Features
- Use divs in HTML contents to ease styling ([2a36a0e](https://github.com/pawamoy/mkdocstrings/commit/2a36a0eba7f52c43a3eba593ddd971acaa0a9c92)).


## [0.4.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.4.0) - 2019-12-22

<small>[Compare with 0.3.0](https://github.com/pawamoy/mkdocstrings/compare/0.3.0...0.4.0)</small>

### Features
- Parse docstrings Google-style blocks, get types from signature ([5af0c7b](https://github.com/pawamoy/mkdocstrings/commit/5af0c7b766ea7158d603b44c6df278dbcd189864)).


## [0.3.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.3.0) - 2019-12-21

<small>[Compare with 0.2.0](https://github.com/pawamoy/mkdocstrings/compare/0.2.0...0.3.0)</small>

### Features
- Allow object referencing in docstrings ([2dd50c0](https://github.com/pawamoy/mkdocstrings/commit/2dd50c06f96acaf0e2f969f217f0cbcfb1de2fd4)).


## [0.2.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.2.0) - 2019-12-15

<small>[Compare with 0.1.0](https://github.com/pawamoy/mkdocstrings/compare/0.1.0...0.2.0)</small>

### Misc
- Refactor, features, etc. ([111fa85](https://github.com/pawamoy/mkdocstrings/commit/111fa85a6305a198ac4e19a75bb491b98683929c)).


## [0.1.0](https://github.com/pawamoy/mkdocstrings/releases/tag/0.1.0) - 2019-12-12

<small>[Compare with first commit](https://github.com/pawamoy/mkdocstrings/compare/f1dd8fb2b4a4ae81f9144fe062ca9743ae82bd69...0.1.0)</small>

### Misc
- Clean up (delete unused files) ([c227043](https://github.com/pawamoy/mkdocstrings/commit/c227043814381b95031e426725e97106931f4ef9)).
- Clean up unused makefile rules ([edc01e9](https://github.com/pawamoy/mkdocstrings/commit/edc01e99aa7b762e800d9ae25cd5b842812dc326)).
- Initial commit ([f1dd8fb](https://github.com/pawamoy/mkdocstrings/commit/f1dd8fb2b4a4ae81f9144fe062ca9743ae82bd69)).
- Update readme ([ae56bdd](https://github.com/pawamoy/mkdocstrings/commit/ae56bdd9ac5692665409e99eb0fd509d8dfc605e)).
- Add plugin ([6ed5cb1](https://github.com/pawamoy/mkdocstrings/commit/6ed5cb1879b498ddc8d0fe1c04db7e3527f2ff81)).
- First PoC, needs better theming ([18a00b9](https://github.com/pawamoy/mkdocstrings/commit/18a00b9405a94405256a1ad2ae45886da40296e4)).
- Get attributes docstrings ([7838fff](https://github.com/pawamoy/mkdocstrings/commit/7838fffa5b1d5a481fd2ea5a94d305a96b06c321)).
- Refactor ([f68f1a8](https://github.com/pawamoy/mkdocstrings/commit/f68f1a89d477a55a6e86a9eb4c92bd5d6416b5cc)).
