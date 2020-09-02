# Building the Python Client

Python 3.7+ is the required version for the client.  The `Pipenv` and `Pipenv.lock` is using
Python 3.7.  Tox tests client with both Python 3.7 and 3.8. We recommend using

### install pyenv

```
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
```

Fix dependencies when installing and building python.

```
sudo apt install libreadline-dev libbz2-dev libsqlite3-dev libffi-dev
```

#### Installing Python 3.7 and 3.8
(Feel free to select later versions of 3.8 if available.)
```
pyenv install 3.7.8
pyenv install 3.7-dev
pyenv install 3.8.3
pyenv install 3.8-dev
```

### Initialize pipenv

`pipenv sync` will install all packages needed from the `Pipenv.lock` file.

`pipenv shell` will open a shell inside the virtual environment.

### Setup git precommit hooks

This repo uses the python `pre-commit` package for pre-commit hooks.  This package and `flake8` should be installed
during the `pipenv sync` above.

Inside the `pipenv`, run `python -m pre-commit install`.

To run the hook outside of git triggered events, you can use:

`pre-commit run` or `pre-commit run --all-files`.  This are also available as part of the Makefile.

### Makefile

Many functions are available in the Makefile.  To see all commands use `make help`.

### Building Distribution package

`python setup.py sdist` will build the Python Client for distributing into `dist/casperlabs_client-X.X.X.tar.gz`.
`make build` performs this command.

The package can be installed for testing with `python -m pip install dist/casperlabs_client-X.X.X.tar.gz`.

If run outside of the pipenv, use `python3.7 -m pip install dist/casperlavs_client-X.X.X.tar.gz`

### Installing Development package

It is best practice to test the installed version of a Python package. The tests have been created to run on the installed version.

Inside the pipenv, run `python setup.py develop` or `make develop`. This makes the `casperlabs_client` library and CLI available, but
will also reference actual source in the package. So changes to source files immediately affect the installed package.
