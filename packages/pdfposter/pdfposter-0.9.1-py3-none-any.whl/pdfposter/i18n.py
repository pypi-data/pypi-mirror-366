# -*- coding: utf-8 -*-
#
# Copyright 2008-2025 by Hartmut Goebel <h.goebel@crazy-compilers.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

__all__ = ["_"]

import gettext
import os
import sys


def install_in_argparse(translate):
    import argparse
    argparse.__dict__['_'] = translate.gettext
    for name in {'gettext', 'lgettext', 'lngettext',
                 'ngettext', 'npgettext', 'pgettext'}:
        if name in argparse.__dict__:
            argparse.__dict__[name] = getattr(translate, name)


_domain = 'pdfposter'
if getattr(sys, 'frozen', None):
    localedir = os.path.join(sys._MEIPASS, 'locale')
else:
    localedir = os.path.join(os.path.dirname(__file__), 'locale')
translate = gettext.translation(_domain,
                                localedir, fallback=True)
_ = translate.gettext

# required to make our translations work in argparse
install_in_argparse(translate)

# Additional string for Python < 3.10:
_('optional arguments')
