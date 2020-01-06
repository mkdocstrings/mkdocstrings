# Contributing
Contributions are welcome, and they are greatly appreciated!

Every little bit helps, and credit will always be given.

For bug reports, feature requests, and feedback,
simply create a new [issue][1].
Try to be as descriptive as possible.

### Bug fixes, new features and documentation
This project is developed using [`poetry`](https://github.com/sdispater/poetry).
Follow the recommended installation method:

```bash
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
```

Then follow these instructions:

1. Fork the repository [on github.com][2];
1. Clone it on your machine;
1. Go into the directory, and run `poetry install` to setup the development environment;
1. Create a new branch with `git checkout -b bug-fix-or-feature-name`;
1. Code!
1. **Write tests. Run them all.** The commands to run the tests are:

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

    A [Makefile](Makefile) is available for convenience: `make test`.

1. When the tests pass, commit
    (make sure to have atomic commits and contextual commit messages!
    [Check out this awesome blog post by Chris Beams for more information.][4])
1. Push;
1. ...and finally, create a new [pull/merge request][5]!
    Make sure to follow the guidelines.

[1]: https://github.com/pawamoy/mkdocstrings/issues/new
[2]: https://github.com/pawamoy/mkdocstrings
[3]: https://docs.pytest.org/en/latest/example/markers.html#using-k-expr-to-select-tests-based-on-their-name
[4]: http://chris.beams.io/posts/git-commit/
[5]: https://github.com/pawamoy/mkdocstrings/compare
