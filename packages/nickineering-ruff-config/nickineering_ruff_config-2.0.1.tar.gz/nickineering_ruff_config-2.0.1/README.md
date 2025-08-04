# Nickineering's Default Ruff Config

![PyPI - Version](https://img.shields.io/pypi/v/nickineering-ruff-config)

A shareable Ruff starting config designed to get as much as possibly from Ruff
quickly.

## Usage

```bash
pip install ruff nickineering-ruff-config
```

Pip install this package, [Ruff](https://docs.astral.sh/ruff/), and create a
`ruff.toml` or another Ruff supported configuration file in your project root.
Inside that file extend this config like so:

```toml
extend = "nickineering-ruff-base.toml"

# Override these settings, or add your own here

# For example:

[format]
docstring-code-format = false
```

You will also need to create a script to copy the file, since Ruff does not
support extending from a package. This is a Poetry script which does that as an
example:

```toml
[tool.poetry.scripts]
update-ruff-base = "nickineering_ruff_config:update_ruff_base"
```

You could then run it with `poetry run update-ruff-base`. This would need to be
re-run to install new versions of this package.

Finally, add the output to your `.gitignore` so you can rely only on the
package.

```gitignore
# Automatically updated configuration file from nickineering-ruff-config
nickineering-ruff-base.toml
```

It is also recommended to create a `Makefile` or other command runner to
document that the update-ruff-base command must be run when installing the
project and so that calls to Ruff run both the lint and format commands. An
example `Makefile` is below:

```makefile
setup:
    poetry install
    poetry run update-ruff-base

lint:
    ruff format
    ruff check --fix
```

## Publishing

A Github Action is automatically run deploying this code to PyPi when a new
release is published in Github.
