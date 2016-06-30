bai-lockbox
===========

A simple parser for files in the BAI lockbox format in order to extract checks
from them.


Installation
------------

To install `bai-lockbox`::

  $ pip install bai-lockbox


Warning
-------

Please be aware that this code was written to the spec that our bank uses, and
has been tested with data that has come from them. This means that there may be
subtle (and maybe some not-so-subtle) differences between the the data we expect
and the data you get. If our parser doesn't read your files, open an issue or
submit a PR. We'd really appreciate it!

Usage
-----

.. code-block:: python

    from lockbox import parse_lockbox_file
    lockbox_file = parse_lockbox_file('/path/to/lockbox.bai')

    for check in lockbox_file.checks:
        print('Received ${} from {} on {}'.format(
            check.amount, check.sender, check.date
        ))


More information can be gathered by looking through the code and reading the
documentation which will be available soon.
