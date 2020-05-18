[![Build Status](
https://travis-ci.com/nickrusso42518/py-auphonic.svg?branch=master)](
https://travis-ci.com/nickrusso42518/py-auphonic)

# Python Library for Auphonic
This Python class simplifies interaction with the Auphonic REST API.
This is useful for podcasters and other professional audio producers
to clean up your audio files before publication.

> Contact information:\
> Email:    njrusmc@gmail.com\
> Twitter:  @nickrusso42518

  * [Usage](#usage)
  * [Methods](#variables)
  * [Reference files](#reference-files)
  * [Testing](#testing)

## Usage
Simply import the `Auphonic` class from the `auphonic.py` module
within your script:

```
from auphonic import Auphonic
auphonic = Auphonic(username="your_account", password="abc123")
```

If you intend to use this program from the shell, you can export these
environment variables. The input directory is optional and will
default to `test_files/` if left unspecified. Output files
are written to a new directory named `auphonic-results/` in your
input directory. This would be `test_files/auphonic-results/`
by default.

```
export AUPHONIC_USERNAME=<your username>
export AUPHONIC_PASSWORD=<your password>
export AUPHONIC_INPUT_DIR=<where to find input files>
```

If you've defined these environment variables, you can save yourself
some Python data loading using the following class-level method:
```
from auphonic import Auphonic
auphonic = Auphonic.build_from_env_vars()
```

With either construction method, you can specify a keyword argument named
`log_level` to set the standard Python logging level. The Auphonic class
only uses `INFO`, but lower level libraries may include `DEBUG` as well.

The `produce.py` script is a sample that consumes the Auphonic class
in a simple and clear way. This is a good starting point to test.

## Methods
To see everything that is available, clone the repository
and use the built-in `help()` function to explore. This will
load a `man` page styled document. There's no point in copying
all the in-code documentation here.

```
>>> import auphonic
>>> help(auphonic)
```

## Reference files
The `data_ref/` directory contains sample JSON responses from the
various HTTP requests. These files are intuitively named and need
no explanation. There are also `.txt` files which represent sample
log outputs to see "what right looks like".

## Testing
To simplify testing both for CI and for manual executions, a GNU Makefile
with phony targets is used. Use the following shortcuts to test the playbook.
It is recommend to run all tests immediately after cloning to save yourself
the pain of discovering bugs during development.
  * `make lint`: Runs `pylint` for linting and `black` for code formatting
  * `make run`: Runs the `produce.py` script and prints the resulting files
  * `make clean`: Removes `*.pyc` files and produced Auphonic files.
     **DO NOT** use this for daily operations, generally only for testing.
  * `make` or `make test`: Runs `clean lint run` in that order
