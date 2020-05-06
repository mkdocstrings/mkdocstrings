# Contributing

Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

## Environment setup

Nothing easier!

Fork and clone the repository, then:

```bash
cd mkdocstrings
make setup
```

That's it!

You now have the dependencies installed.

Run `make help` to see all the available actions!

## Development

As usual:

1. create a new branch: `git checkout -b feature-or-bugfix-name`
1. edit the code and/or the documentation

If you updated the documentation or the project dependencies:

1. run `make docs-regen`
1. run `make docs-serve`,
   go to http://localhost:8000 and check that everything looks good

**Before committing:**

1. run `make format` to auto-format the code
1. run `make check` to check everything (fix any warning)
1. run `make test` to run the tests (fix any issue)
1. follow our [commit message convention](#commit-message-convention)

If you are unsure about how to fix or ignore a warning,
just let the continuous integration fail,
and we will help you during review.

Don't bother updating the changelog, we will take care of this.

## Commit message convention

Commits messages must follow the
[Angular style](https://gist.github.com/stephenparish/9941e89d80e2bc58a153#format-of-the-commit-message):

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
- `style`: A change in code style/format.
- `tests`: About tests.

**Subject (and body) must be valid Markdown.**
If you write a body, please add issues references at the end:

```
Body.

References: #10, #11.
Fixes #15.
```

## Pull requests guidelines

Link to any related issue in the Pull Request message.

During review, we recommend using fixups:

```bash
# SHA is the SHA of the commit you want to fix
git commit --fixup=SHA
```

Once all the changes are approved, you can squash your commits:

```bash
git rebase -i --autosquash master
```

And force-push:

```bash
git push -f
```

If this seems all too complicated, you can push or force-push each new commit,
and we will squash them ourselves if needed, before merging.
