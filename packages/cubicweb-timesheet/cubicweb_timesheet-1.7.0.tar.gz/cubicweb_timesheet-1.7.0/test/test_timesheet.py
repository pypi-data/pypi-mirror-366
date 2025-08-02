"""template automatic tests"""

from cubicweb_web.devtools.testlib import AutomaticWebTest


class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(("Activity", "Resource", "Resourcetype"))

    def list_startup_views(self):
        # XXX needs to specify req.form['project'| 'workcase'] to test
        # [prj-]acstats views
        return ("index",)  # 'actstats', 'prj-actstats'


if __name__ == "__main__":
    import unittest

    unittest.main()
