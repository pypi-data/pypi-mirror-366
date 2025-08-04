.. This file is part of pdfposter.
   Copyright (C) 2008-2025 Hartmut Goebel
   Licensed under the GNU Free Documentation License v1.3 or any later version.
   SPDX-License-Identifier: GFDL-1.3-or-later

Frequently Asked Questions
===============================

* *How can I suppress these superfluous empty pages?*

  *Short Answer:* Specify the desired output size using the same
  page-name as the medium-size::

     pdfposter -mA5 -p2xA5 in.pdf out.pdf

  *Long Answer*: If you are running::

     pdfposter -mA5 -pA4 in.pdf out.pdf

  you most probably expect the result to be 2 A5-pages large, but you
  will get *three* pages, where the third seams to be empty. (If you
  have a full-colored background, you will find a small line on the
  third page.)

  And this is what went wrong:

  In the command above, you *say*: "The output should be A4 sized",
  while you *mean*: "The output should fit on two A5 pages".

  Basically you are right, if you say "hey, this ought to be the
  same!". It is a scaling or rounding issue caused by ISO page sizes
  not scaling exactly (even as they should, see `ISO 216
  <https://en.wikipedia.org/wiki/ISO_216>`_). For example since A4 is
  297 mm high, A5 should be 148.5 mm wide, but is only 148 mm wide.

  So the solution is to specify on the command-line what you want:
  "should fit on two A5 pages"::

         pdfposter -mA5 -p2xA5 in.pdf out.pdf


* Are there other Python tools for manipulating PDF?

  Yes, there are:

  * `pdfbook <https://pdfbook.readthedocs.io/>`_
  * `pdfdecrypt <https://pdfdecrypt.readthedocs.io/>`_
  * `pdfjoin <https://pdfjoin.readthedocs.io/>`_
  * `flyer-composer <http://www.crazy-compilers.com/flyer-composer.html>`_
     (including an optional Qt GUI)

  * `pdfnup <https://pypi.org/project/pdfnup/>`_
  * `pdfsplit <https://pypi.org/project/pdfsplit/>`_
  * `pdfgrid <https://pypi.org/project/pdfgrid/>`_


.. include:: _common_definitions.txt
