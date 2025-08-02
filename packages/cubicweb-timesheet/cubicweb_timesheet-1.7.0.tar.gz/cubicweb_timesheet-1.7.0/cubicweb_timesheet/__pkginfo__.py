# pylint: disable-msg=W0622
"""cubicweb-timesheet application packaging information"""

modname = "timesheet"
distname = "cubicweb-%s" % modname

numversion = (1, 7, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
description = "record who did what and when for the CubicWeb framework"
web = "http://www.cubicweb.org/project/%s" % distname
author = "Logilab"
author_email = "contact@logilab.fr"
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">= 4.10.0, < 6.0.0",
    "cubicweb-web": ">= 1.6.0, < 2.0.0",
    "cubicweb-calendar": ">= 1.1.0, < 2.0.0",
    "cubicweb-workorder": ">= 1.1.0, < 2.0.0",
}
