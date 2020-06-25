# Building the Python Client

Python 3.7 is the required version for the client. There are some changes that will be made using 3.7+ features.
Currently there is a bug with Goggle's proto files we use in Python 3.8. The `Pipenv` and `Pipenv.lock` is using
Python 3.7.

### Requirements

Compilation is needed for some of the cryptography dependencies for the client, so `python3.7-dev` should be installed
with `sudo apt install python3.7-dev`.

We use `pipenv` for the virtual environment. This isolates installed packages for the client from your system
python install. This can be installed on Debian based systems with `sudo apt install pipenv`.

`pipenv` is installed to the user's `.local/bin` folder. This will not be accessible without adding your
`~/.local/bin` folder to `$PATH` in `.bashrc` or with other means.

### Initialize pipenv

`pipenv sync` will install all packages needed from the `Pipenv.lock` file.

`pipenv shell` will open a shell inside the virtual environment.

### Setup git precommit hooks

This repo uses the python `pre-commit` package for pre-commit hooks.  This package and `flake8` should be installed
during the `pipenv sync` above.  

Inside the `pipenv`, run `python -m pre-commit install`.

To run the hook outside of git triggered events, you can use:

`pre-commit run` or `pre-commit run --all-files`. 

### CasperLabs repo dependency

Building this package depends on the `proto` files available in the CasperLabs repo.  This is expected
to be in the same level directory of `client-py` repo.  

For running tests inside `manual-test`, the `CasperLabs/hack/docker` network stand-up is used.  This expects
all of the prerequisites to run `make docker-build-all` in the root of `CasperLabs` repo as well as 
`make contracts-rs` in `CasperLabs/execution-engine` for some `.wasm` contracts that are used in testing.

### Building Distribution package

`python setup.py sdist` will build the Python Client for distributing into `dist/casperlabs_client-X.X.X.tar.gz`.
`build.sh` performs a `pipenv sync` then this command, after verifying included .wasm files exist.

The package can be installed for testing with `python -m pip install dist/casperlabs_client-X.X.X.tar.gz`.

If run outside of the pipenv, use `python3.7 -m pip install dist/casperlavs_client-X.X.X.tar.gz`

### Building Development package

It is best practice to test the installed version of a Python package. The tests have been created to run on the installed version.

Inside the pipenv, run `python setup.py develop`. This makes the `casperlabs_client` library and CLI available, but
will also reference actual source in the package. So changes to source files immediately affect the installed package.
