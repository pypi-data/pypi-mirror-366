#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pkg_resources import get_distribution

from magma_ven.download import Download
from magma_ven.magma_ven import MagmaVen

__version__ = get_distribution("magma-ven").version
__author__ = "Martanto"
__author_email__ = "martanto@live.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2024, MAGMA Indonesia"
__url__ = "https://github.com/martanto/magma-ven"

__all__ = [
    "__version__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "MagmaVen",
    "Download",
]
