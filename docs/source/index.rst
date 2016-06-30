.. bai-lockbox documentation master file, created by
   sphinx-quickstart on Fri Jun 24 16:03:25 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

bai-lockbox
===========

v\ |version|

bai-lockbox is a handy Python parser for the BAI Lockbox format. There
isn't a huge amount to say about it beyond that. You'll probably want
to check out the :ref:`Quick Start<quick-start>` to see how to use
it.

.. _quick-start:

Quickstart
----------

Using this library is pretty simple - the following code block has just about
all of the functionality offered.

.. code-block:: python

    from lockbox.parser import LockboxFile
    with open('/path/to/file', 'r') as inf:
        lockbox_file = LockboxFile.from_file(inf)

    for check in lockbox_file.checks:
        print('Received ${} from {} on {}'.format(
            check.amount, check.sender, check.date
        ))

The `checks` field of a :class:`~lockbox.parser.LockboxFile` is just a list of
:class:`~lockbox.parser.Check` objects.


.. automodule:: lockbox.parser
   :members:


.. automodule:: lockbox.records
   :members:


Indices and tables
==================

* :ref:`search`
