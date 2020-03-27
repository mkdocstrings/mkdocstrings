# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [v0.9.1](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.9.1) - 2020-03-21

<small>[Compare with v0.9.0](https://github.com/pawamoy/mkdocstrings/compare/v0.9.0...v0.9.1)</small>

### Bug fixes
- Fix cross-references when deploying to GitHub pages ([36f804b](https://github.com/pawamoy/mkdocstrings/commit/36f804beab01531c0331ed89d21f3e5e15bd8585)).

## [v0.9.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.9.0) - 2020-03-21

<small>[Compare with v0.8.0](https://github.com/pawamoy/mkdocstrings/compare/v0.8.0...v0.9.0)</small>
 
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


## [v0.8.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.8.0) - 2020-03-04

<small>[Compare with v0.7.2](https://github.com/pawamoy/mkdocstrings/compare/v0.7.2...v0.8.0)</small>

### Breaking Changes
- Be compatible with Mkdocs >= 1.1 ([5a974a4](https://github.com/pawamoy/mkdocstrings/commit/5a974a4eb810904d6836e216d8539affc8acaa6f)).
  This is a breaking change as we're not compatible with versions of Mkdocs below 1.1 anymore. 
  If you cannot upgrade Mkdocs to 1.1, pin mkdocstrings' version to 0.7.2.

## [v0.7.2](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.7.2) - 2020-03-04

<small>[Compare with v0.7.1](https://github.com/pawamoy/mkdocstrings/compare/v0.7.1...v0.7.2)</small>

### Bug Fixes
- Catch `OSError` when trying to get source lines ([8e8d604](https://github.com/pawamoy/mkdocstrings/commit/8e8d604ba95363c140841c84535d2350d7ebbfe3)).
- Do not render signature empty sentinel ([16dfd73](https://github.com/pawamoy/mkdocstrings/commit/16dfd73cf30d01314dba756d3f10308b99c87dcc)).
- Fix for nested classes and their attributes ([7fef903](https://github.com/pawamoy/mkdocstrings/commit/7fef9037c5299d6106347b0db29f85a644f85c16)).
- Fix `relative_file_path` method ([52715ad](https://github.com/pawamoy/mkdocstrings/commit/52715adc59fe2e26a9e91df88bac8b8b32d4635e)).
- Wrap file path in backticks to escape it ([2525f39](https://github.com/pawamoy/mkdocstrings/commit/2525f39ad8c181679fa33db8e6dfaa28eb39c289)).

## [v0.7.1](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.7.1) - 2020-02-18

<small>[Compare with v0.7.0](https://github.com/pawamoy/mkdocstrings/compare/v0.7.0...v0.7.1)</small>

### Bug Fixes
- Replace literal slash with os.sep for Windows compatibility ([70f9af5](https://github.com/pawamoy/mkdocstrings/commit/70f9af5e33cda694cda33870c84a770c853d84b5)).


## [v0.7.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.7.0) - 2020-01-13

<small>[Compare with v0.6.1](https://github.com/pawamoy/mkdocstrings/compare/v0.6.1...v0.7.0)</small>

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


## [v0.6.1](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.6.1) - 2020-01-02

<small>[Compare with v0.6.0](https://github.com/pawamoy/mkdocstrings/compare/v0.6.0...v0.6.1)</small>

### Bug Fixes
- Break docstring discarding loop if found ([5a17fec](https://github.com/pawamoy/mkdocstrings/commit/5a17fec5beed2003d19ccdcb359b46b79bfcf469)).
- Fix discarding docstring ([143f7cb](https://github.com/pawamoy/mkdocstrings/commit/143f7cb00f02a7d3179cc5606ed7903566250227)).
- Fix getting annotation from nodes ([ecde72b](https://github.com/pawamoy/mkdocstrings/commit/ecde72bb22ccedb36aa847dd50504c63ad04498c)).
- Fix various things ([affbf06](https://github.com/pawamoy/mkdocstrings/commit/affbf064d457d4b626e8f67d38e94d7919bc2df2)).

### Code Refactoring
- Break as soon as we find the same attr in a parent class while trying to discard the docstring ([65d7908](https://github.com/pawamoy/mkdocstrings/commit/65d7908f489ec465b2803ea8f55c70d0f9d7586b)).
- Split Docstring.parse method to improve readability ([2226e2d](https://github.com/pawamoy/mkdocstrings/commit/2226e2d55a6b9bbdd5a56183f1a9ba3c5f01b5ac)).


## [v0.6.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.6.0) - 2019-12-28

<small>[Compare with v0.5.0](https://github.com/pawamoy/mkdocstrings/compare/v0.5.0...v0.6.0)</small>

### Bug Fixes
- Fix GenericMeta import error on Python 3.7+ ([febf2b9](https://github.com/pawamoy/mkdocstrings/commit/febf2b9749d97cce80f5d20339372842fdffc908)).

### Code Refactoring
- More classes. Still ugly code though :'( ([f41c119](https://github.com/pawamoy/mkdocstrings/commit/f41c11988d8d849a0310cca511c2d93a74cab86f)).
- Split into more modules ([f1872a4](https://github.com/pawamoy/mkdocstrings/commit/f1872a4c8d41a0b9603b7f344de3186110a4e1bd)).
- Use Object subclasses ([40dd106](https://github.com/pawamoy/mkdocstrings/commit/40dd1062188e6ad6ef6fbc12ddead2132fe6af1e)).


## [v0.5.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.5.0) - 2019-12-22

<small>[Compare with v0.4.0](https://github.com/pawamoy/mkdocstrings/compare/v0.4.0...v0.5.0)</small>

### Features
- Use divs in HTML contents to ease styling ([2a36a0e](https://github.com/pawamoy/mkdocstrings/commit/2a36a0eba7f52c43a3eba593ddd971acaa0a9c92)).


## [v0.4.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.4.0) - 2019-12-22

<small>[Compare with v0.3.0](https://github.com/pawamoy/mkdocstrings/compare/v0.3.0...v0.4.0)</small>

### Features
- Parse docstrings Google-style blocks, get types from signature ([5af0c7b](https://github.com/pawamoy/mkdocstrings/commit/5af0c7b766ea7158d603b44c6df278dbcd189864)).


## [v0.3.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.3.0) - 2019-12-21

<small>[Compare with v0.2.0](https://github.com/pawamoy/mkdocstrings/compare/v0.2.0...v0.3.0)</small>

### Features
- Allow object referencing in docstrings ([2dd50c0](https://github.com/pawamoy/mkdocstrings/commit/2dd50c06f96acaf0e2f969f217f0cbcfb1de2fd4)).


## [v0.2.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.2.0) - 2019-12-15

<small>[Compare with v0.1.0](https://github.com/pawamoy/mkdocstrings/compare/v0.1.0...v0.2.0)</small>

### Misc
- Refactor, features, etc. ([111fa85](https://github.com/pawamoy/mkdocstrings/commit/111fa85a6305a198ac4e19a75bb491b98683929c)).


## [v0.1.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.1.0) - 2019-12-12

<small>[Compare with first commit](https://github.com/pawamoy/mkdocstrings/compare/f1dd8fb2b4a4ae81f9144fe062ca9743ae82bd69...v0.1.0)</small>

### Misc
- Clean up (delete unused files) ([c227043](https://github.com/pawamoy/mkdocstrings/commit/c227043814381b95031e426725e97106931f4ef9)).
- Clean up unused makefile rules ([edc01e9](https://github.com/pawamoy/mkdocstrings/commit/edc01e99aa7b762e800d9ae25cd5b842812dc326)).
- Initial commit ([f1dd8fb](https://github.com/pawamoy/mkdocstrings/commit/f1dd8fb2b4a4ae81f9144fe062ca9743ae82bd69)).
- Update readme ([ae56bdd](https://github.com/pawamoy/mkdocstrings/commit/ae56bdd9ac5692665409e99eb0fd509d8dfc605e)).
- Add plugin ([6ed5cb1](https://github.com/pawamoy/mkdocstrings/commit/6ed5cb1879b498ddc8d0fe1c04db7e3527f2ff81)).
- First PoC, needs better theming ([18a00b9](https://github.com/pawamoy/mkdocstrings/commit/18a00b9405a94405256a1ad2ae45886da40296e4)).
- Get attributes docstrings ([7838fff](https://github.com/pawamoy/mkdocstrings/commit/7838fffa5b1d5a481fd2ea5a94d305a96b06c321)).
- Refactor ([f68f1a8](https://github.com/pawamoy/mkdocstrings/commit/f68f1a89d477a55a6e86a9eb4c92bd5d6416b5cc)).


