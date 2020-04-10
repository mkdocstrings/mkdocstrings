# Contributing

Contributions are welcome, and they are greatly appreciated!

Every little bit helps, and credit will always be given.

For bug reports, feature requests, and feedback,
simply create a new [issue][1].
Try to be as descriptive as possible.

## Setup

This project is developed using [`poetry`](https://github.com/sdispater/poetry).
Follow the recommended installation method:

```bash
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
```

...or install it with [`pipx`](https://github.com/pipxproject/pipx):

```
pipx install poetry
```

Then follow these instructions:

1. Fork the repository [on github.com][2];
1. Clone it on your machine;
1. Go into the directory, and run `poetry install` to install all the dependencies into a new virtualenv.

## New feature or bug fix

1. Create a new branch with `git checkout -b bug-fix-or-feature-name`;
1. Code!
1. **Write tests. Run them all.**
1. **Run the quality checks.**

## Running quality checks

The command to check the project's quality checks is:

```
make check
```

*Type `make` to see all the available rules.*

## Running tests

The command to run the tests is:

```
make test
```

*Type `make` to see all the available rules.*

For more flexibility:

```bash
poetry run pytest  # to run all tests sequentially
poetry run pytest -v  # to print one test per line
poetry run pytest -n 4  # to run tests in parallel (4 workers)
poetry run pytest tests/test_api.py  # to run tests in a specific file
```

`pytest` provides the `-k` option to select tests based on their names:

```bash
poetry run pytest -k "api and remove"
poetry run pytest -k "utils or stats"
```

See the [documentation for the `-k` option][3] for more examples.

## Commits messages

Make sure to have atomic commits and contextual commit messages!
[Check out this blog post by Chris Beams for more information][4].

Commits messages must follow the [Angular style](https://gist.github.com/stephenparish/9941e89d80e2bc58a153#format-of-the-commit-message):

```
<type>[(scope)]: Subject

[Body]
```

Scope and body are optional. Type can be:

- `build`: About packaging, building wheels, etc.
- `chore`: About packaging or repo/files management.
- `ci`: About Continuous Integration.
- `docs`: About documentation.
- `feat`: New feature.
- `fix`: Bug fix.
- `perf`: About performance.
- `refactor`: Changes which are not features nor bug fixes.
- `revert`: When reverting a commit.
- `style`: A change in code style/format.
- `tests`: About tests.

Subject (and body) must be valid Markdown. If you write a body, please add issues references at the end:

```
Body.

References: #10, #11.
Fixes #15.
```

## Pull Requests

Push your code, and finally create a new [pull request][5].
Make sure to follow the guidelines.

[1]: https://github.com/pawamoy/mkdocstrings/issues/new
[2]: https://github.com/pawamoy/mkdocstrings
[3]: https://docs.pytest.org/en/latest/example/markers.html#using-k-expr-to-select-tests-based-on-their-name
[4]: http://chris.beams.io/posts/git-commit/
[5]: https://github.com/pawamoy/mkdocstrings/compare
