.. This file is part of pdfposter.
   Copyright (C) 2008-2025 Hartmut Goebel
   Licensed under the GNU Free Documentation License v1.3 or any later version.
   SPDX-License-Identifier: GFDL-1.3-or-later


Download & Installation
=========================

Instructions for Windows Users
-----------------------------------

1. |pdfposter| requires Python. If you don't have Python installed already,
   download and install Python 3.13 from https://python.org/download/3.13/

   During installation, make sure to check "Include into PATH".

2. If you already have Python installed, please check that your Python
   directory (normally :file:`C:\\Python313` for python 3.13) and the Python
   Scripts directory (normally :file:`C:\\Python313\\Scripts`) are in the system
   path. If not, just add them in :menuselection:`My Computer --> Properties
   --> Advanced --> Environment Variables` to the :envvar:`Path` system
   variable.

3. Install |pdfposter| by running ::

     pip install pdfposter

   Then run the console command ``pdfposter --help`` to get detailed help.

   If the command ``pip`` is unknown to you system, please refer to the
   `pip homepage <https://pip.pypa.io/en/stable/installing/>`_ for help.


Instructions for GNU/Linux and other Operating Systems
--------------------------------------------------------

Most current GNU/Linux distributions provide packages for |pdfposter|.
Simply search your distribution's software catalog.

Also many vendors provide Python, and some even provide |pdfposter|.
Please check your vendor's software repository.

If your distribution or vendor does not provide a current version of
|pdfposter| please read on.

If your vendor does not provide :command:`python`
please download Python 3.13 from https://www.python.org/download/ and
follow the installation instructions there.

If you distribution or vendor missed providing :command:`pip`,
alongside :command:`python`,
please check your vendor's or distribution's software repository
for a package called `pip` or `python-pip`.
If this is not provided, please refer to the
`pip homepage <https://pip.pypa.io/en/stable/installing/>`_ for help.


Optionally you might want to install `pypdf`
- which is a requirement for |pdfposter| -
provided by your distribution or vendor
so at least this package will be maintained by your distribution.
Check for a package named ``python3-pypdf`` or that like.

Then continue with :ref:`installing pdfposter` below.


.. _installing pdfposter:

Installing |pdfposter| using :command:`pip`
---------------------------------------------

After installing `Python` (and optionally `pypdf`), just run::

  sudo pip install pdfposter

to install |pdfposter| for all users.
For installing |pdfposter| for yourself only, run::

  pip install --user pdfposter

If your system does not have network access
  
- download |pdfposter| from https://pypi.org/project/pdfposter/,

- download `pypdf` from https://pypi.org/project/pypdf/, and

- run ::

    sudo pip install pdfposter-*.tar.gz pypdf-*.tar.gz

  respective ::

    pip install --user pdfposter-*.tar.gz pypdf-*.tar.gz


.. include:: _common_definitions.txt

