[![Build Status](
https://travis-ci.com/nickrusso42518/py-auphonic.svg?branch=master)](
https://travis-ci.com/nickrusso42518/py-auphonic)

# Python Library for Auphonic
This Python class simplifies interaction with the Auphonic REST API.
This is useful for podcasters and other professional audio producers
to clean up your audio files before publication.

## Usage
Simply import the `Auphonic` class from the `auphonic.py` module
within your script:

```
from auphonic import Auphonic
auphonic = Auphonic(username="your_account", password="abc123")
```

If you intend to use this program from the shell, you can export these
environment variables. The input directory is optional and will
default to `~/Desktop/auphonic` if left unspecified. Output files
are written to a new directory named `auphonic-results` in your
input directory.

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
`debug` to enable timestamped logging to `stderr`; `True` enables this
logging (default) while `False` disables it.

The `produce.py` script is a sample that consumes the Auphonic class
in a simple and clear way. This is a good starting point to test.

## More details
To see everything that is available, clone the repository
and use the built-in `help()` function to explore. This will
load a `man` page styled document. There's no point in copying
all the in-code documentation here.

```
>>> import auphonic
>>> help(auphonic)
```
