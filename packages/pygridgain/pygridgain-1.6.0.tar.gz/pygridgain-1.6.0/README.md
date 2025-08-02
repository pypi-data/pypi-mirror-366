# pygridgain
GridGain Community Edition thin (binary protocol) client, written in Python 3.

## Prerequisites

- Python 3.9 or above (3.9, 3.10, 3.11, 3.12 and 3.13 are tested),
- Access to GridGain node, local or remote. The current thin client
  version was tested on GridGain CE 8.8 and 8.9 (binary client protocol 1.7.1).

## Installation

### From repository
This is a recommended way for users. If you only want to use the `pygridgain`
module in your project, do:
```
$ pip install pygridgain
```

### From sources
This way is more suitable for developers or if you install client from zip archive.
1. Download and/or unzip GridGain Python client sources to `gridgain_client_path`
2. Go to `gridgain_client_path` folder
3. Execute `pip install -e .`

```bash
$ cd <gridgain_client_path>
$ pip install -e .
```

This will install the repository version of `pygridgain` into your environment
in so-called “develop” or “editable” mode. You may read more about
[editable installs](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs)
in the `pip` manual.

Then run through the contents of `requirements` folder to install
the additional requirements into your working Python environment using
```
$ pip install -r requirements/<your task>.txt
```

You may also want to consult the `setuptools` manual about using `setup.py`.

### *optional C extension*
There is an optional C extension to speedup some computational intensive tasks. If it's compilation fails
(missing compiler or CPython headers), `pygridgain` will be installed without this module.

- On Linux or MacOS X only C compiler is required (`gcc` or `clang`). It compiles during standard setup process.
- For building universal `wheels` (binary packages) for Linux, just invoke script `./scripts/create_distr.sh`. 
  
  ***NB!* Docker is required.**
  
- On Windows MSVC 14.x required, and it should be in path, also python versions 3.9, 3.10, 3.11, 3.12 and 3.13 both for x86 and
  x86-64 should be installed. You can disable some of these versions but you'd need to edit script for that.
- For building `wheels` for Windows, invoke script `.\scripts\BuildWheels.ps1` using PowerShell. Just make sure that
  your execution policy allows execution of scripts in your environment.
  
  Ready wheels for `x86` and `x86-64` for different python versions (3.9, 3.10, 3.11, 3.12 and 3.13) will be
  located in `distr` directory.

### Updating from older version

To upgrade an existing package, use the following command:
```
pip install --upgrade pygridgain
```

To install the latest version of a package:

```
pip install pygridgain
```

To install a specific version:

```
pip install pygridgain==1.5.0
```

## Documentation
[The package documentation](https://pygridgain.readthedocs.io) is available
at *RTD* for your convenience.

If you want to build the documentation from source, do the developer
installation as described above, then run the following commands:
```
$ pip install -r requirements/docs.txt
$ cd docs
$ make html
```

Then open `<client_root_directory>/docs/generated/html/index.html`
in your browser.

## Examples
Some examples of using pygridgain are provided in
`examples` folder. They are extensively commented in the
“[Examples of usage](https://pygridgain.readthedocs.io/en/latest/examples.html)”
section of the documentation.

This code implies that it is run in the environment with `pygridgain` package
installed, and GridGain node is running on localhost:10800.

## Testing
*NB!* It is recommended installing `pygridgain` in development mode.
Refer to [this section](#from-sources) for instructions.

Do not forget to install test requirements: 
```bash
$ pip install -r requirements/install.txt -r requirements/tests.txt
```

Also, you'll need to have a binary release of Ignite with `log4j2` enabled and to set
`IGNITE_HOME` environment variable: 
```bash
$ cd <gridgain_binary_release>
$ export IGNITE_HOME=$(pwd)
$ cp -r $IGNITE_HOME/libs/optional/ignite-log4j2 $IGNITE_HOME/libs/
```
### Run basic tests
```bash
$ pytest
```
### Run with examples
```bash
$ pytest --examples 
```

If you need to change the connection parameters, see the documentation on
[testing](https://pygridgain.readthedocs.io/en/latest/readme.html#testing).
