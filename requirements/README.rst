``requirements/``
#################

This directory contains the files that manage dependencies for the project.

Each subdirectory in this directory contains a ``pyproject.toml`` file
with purpose-specific dependencies listed.


How it's used
=============

Tox is configured to use the exported ``requirements.txt`` files as needed.
This helps ensure reproducibility.


How it's updated
================

A tox label, ``update``, ensures that dependencies can be easily updated,
and that ``requirements.txt`` files are consistently re-exported.

This can be invoked by running:

..  code-block::

    tox run -m update


How to add dependencies
=======================

New dependencies can be added to a given subdirectory's ``pyproject.toml``
by either manually modifying the file, or by running a command like:

..  code-block::

    poetry add --lock --directory "requirements/$DIR" $DEPENDENCY_NAME

Either way, the dependencies must be re-exported:

..  code-block::

    tox run -m update
