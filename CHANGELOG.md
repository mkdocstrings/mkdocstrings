# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [v0.7.1](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.7.1) ([compare](https://github.com/pawamoy/mkdocstrings/compare/v0.7.0...v0.7.1)) - 2020-02-18

### Bug Fixes
- Replace literal slash with os.sep for Windows compatibility ([70f9af5](https://github.com/pawamoy/mkdocstrings/commit/70f9af5e33cda694cda33870c84a770c853d84b5)).


## [v0.7.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.7.0) ([compare](https://github.com/pawamoy/mkdocstrings/compare/v0.6.1...v0.7.0)) - 2020-01-13

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


## [v0.6.1](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.6.1) ([compare](https://github.com/pawamoy/mkdocstrings/compare/v0.6.0...v0.6.1)) - 2020-01-02

### Bug Fixes
- Break docstring discarding loop if found ([5a17fec](https://github.com/pawamoy/mkdocstrings/commit/5a17fec5beed2003d19ccdcb359b46b79bfcf469)).
- Fix discarding docstring ([143f7cb](https://github.com/pawamoy/mkdocstrings/commit/143f7cb00f02a7d3179cc5606ed7903566250227)).
- Fix getting annotation from nodes ([ecde72b](https://github.com/pawamoy/mkdocstrings/commit/ecde72bb22ccedb36aa847dd50504c63ad04498c)).
- Fix various things ([affbf06](https://github.com/pawamoy/mkdocstrings/commit/affbf064d457d4b626e8f67d38e94d7919bc2df2)).

### Code Refactoring
- Break as soon as we find the same attr in a parent class while trying to discard the docstring ([65d7908](https://github.com/pawamoy/mkdocstrings/commit/65d7908f489ec465b2803ea8f55c70d0f9d7586b)).
- Split Docstring.parse method to improve readability ([2226e2d](https://github.com/pawamoy/mkdocstrings/commit/2226e2d55a6b9bbdd5a56183f1a9ba3c5f01b5ac)).


## [v0.6.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.6.0) ([compare](https://github.com/pawamoy/mkdocstrings/compare/v0.5.0...v0.6.0)) - 2019-12-28

### Bug Fixes
- Fix GenericMeta import error on Python 3.7+ ([febf2b9](https://github.com/pawamoy/mkdocstrings/commit/febf2b9749d97cce80f5d20339372842fdffc908)).

### Code Refactoring
- More classes. Still ugly code though :'( ([f41c119](https://github.com/pawamoy/mkdocstrings/commit/f41c11988d8d849a0310cca511c2d93a74cab86f)).
- Split into more modules ([f1872a4](https://github.com/pawamoy/mkdocstrings/commit/f1872a4c8d41a0b9603b7f344de3186110a4e1bd)).
- Use Object subclasses ([40dd106](https://github.com/pawamoy/mkdocstrings/commit/40dd1062188e6ad6ef6fbc12ddead2132fe6af1e)).


## [v0.5.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.5.0) ([compare](https://github.com/pawamoy/mkdocstrings/compare/v0.4.0...v0.5.0)) - 2019-12-22

### Features
- Use divs in HTML contents to ease styling ([2a36a0e](https://github.com/pawamoy/mkdocstrings/commit/2a36a0eba7f52c43a3eba593ddd971acaa0a9c92)).


## [v0.4.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.4.0) ([compare](https://github.com/pawamoy/mkdocstrings/compare/v0.3.0...v0.4.0)) - 2019-12-22

### Features
- Parse docstrings Google-style blocks, get types from signature ([5af0c7b](https://github.com/pawamoy/mkdocstrings/commit/5af0c7b766ea7158d603b44c6df278dbcd189864)).


## [v0.3.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.3.0) ([compare](https://github.com/pawamoy/mkdocstrings/compare/v0.2.0...v0.3.0)) - 2019-12-21

### Features
- Allow object referencing in docstrings ([2dd50c0](https://github.com/pawamoy/mkdocstrings/commit/2dd50c06f96acaf0e2f969f217f0cbcfb1de2fd4)).


## [v0.2.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.2.0) ([compare](https://github.com/pawamoy/mkdocstrings/compare/v0.1.0...v0.2.0)) - 2019-12-15

### Misc
- Refactor, features, etc. ([111fa85](https://github.com/pawamoy/mkdocstrings/commit/111fa85a6305a198ac4e19a75bb491b98683929c)).


## [v0.1.0](https://github.com/pawamoy/mkdocstrings/releases/tag/v0.1.0) ([compare](https://github.com/pawamoy/mkdocstrings/compare/f1dd8fb2b4a4ae81f9144fe062ca9743ae82bd69...v0.1.0)) - 2019-12-12

### Misc
- Clean up (delete unused files) ([c227043](https://github.com/pawamoy/mkdocstrings/commit/c227043814381b95031e426725e97106931f4ef9)).
- Clean up unused makefile rules ([edc01e9](https://github.com/pawamoy/mkdocstrings/commit/edc01e99aa7b762e800d9ae25cd5b842812dc326)).
- Initial commit ([f1dd8fb](https://github.com/pawamoy/mkdocstrings/commit/f1dd8fb2b4a4ae81f9144fe062ca9743ae82bd69)).
- Update readme ([ae56bdd](https://github.com/pawamoy/mkdocstrings/commit/ae56bdd9ac5692665409e99eb0fd509d8dfc605e)).
- Add plugin ([6ed5cb1](https://github.com/pawamoy/mkdocstrings/commit/6ed5cb1879b498ddc8d0fe1c04db7e3527f2ff81)).
- First PoC, needs better theming ([18a00b9](https://github.com/pawamoy/mkdocstrings/commit/18a00b9405a94405256a1ad2ae45886da40296e4)).
- Get attributes docstrings ([7838fff](https://github.com/pawamoy/mkdocstrings/commit/7838fffa5b1d5a481fd2ea5a94d305a96b06c321)).
- Refactor ([f68f1a8](https://github.com/pawamoy/mkdocstrings/commit/f68f1a89d477a55a6e86a9eb4c92bd5d6416b5cc)).


