==========================
pdfposter
==========================

-------------------------------------------------------------
Scale and tile PDF images/pages to print on multiple pages.
-------------------------------------------------------------

:Author:    Hartmut Goebel <h.goebel@crazy-compilers.com>
:Version:   Version 0.9.1
:Copyright: 2008-2025 by Hartmut Goebel
:License:   GNU Public License v3 or later (GPL-3.0-or-later)
:Homepage:  https://pdfposter.readthedocs.io/

``Pdfposter`` can be used to create a large poster by building it from
multiple pages and/or printing it on large media. It expects as input a
PDF file, normally printing on a single page. The output is again a
PDF file, maybe containing multiple pages together building the
poster.
The input page will be scaled to obtain the desired size.

This is much like ``poster`` does for Postscript files, but working
with PDF. Since sometimes poster does not like your files converted
from PDF. :-) Indeed ``pdfposter`` was inspired by ``poster``.

For more information please refer to the manpage or visit
the `project homepage <https://pdfposter.readthedocs.io/>`_.


Translating Weblate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Pdfposter`` and its siblings are continually being translated
using `Codeberg Translate`__.
Feel free to take your part in the effort of making ``pdfposter`` available
in as many human languages as possible.
It brings ``pdfposter`` closer to its users!

__ https://translate.codeberg.org/projects/pdftools/


Requirements and Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Pdfposter`` requires

* `Python`__  (3.8—3.13, but newer versions should work, too),
* `pip`__ for installation, and
* `pypdf`__ (5.5 or newer, tested with 5.8.0)

__ https://www.python.org/download/
__ https://pypi.org/project/pip
__ https://pypi.org/project/pypdf

.. This file is part of pdfposter.
   Copyright (C) 2008-2025 Hartmut Goebel
   Licensed under the GNU Free Documentation License v1.3 or any later version.
   SPDX-License-Identifier: GFDL-1.3-or-later

.. Emacs config:
 Local Variables:
 mode: rst
 End:
