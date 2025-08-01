# pylint: disable=W0622
"""cubicweb-rqlcontroller application packaging information"""

modname = "rqlcontroller"
distname = "cubicweb-rqlcontroller"

numversion = (1, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "restfull RQL edition capabilities for CubicWeb"
web = f"https://forge.extranet.logilab.fr/cubicweb/cubes/{distname}"

__depends__ = {
    "cubicweb": ">= 4.5.3, < 6.0.0",
    "cubicweb-web": ">= 1.6.1, < 2.0.0",
}
__recommends__ = {}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: JavaScript",
]
