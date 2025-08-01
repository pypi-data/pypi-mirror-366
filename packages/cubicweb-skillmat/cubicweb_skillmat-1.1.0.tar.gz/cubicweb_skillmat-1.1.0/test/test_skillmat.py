import unittest
from cubicweb_web.devtools.testlib import AutomaticWebTest


class AutomaticWebTest(AutomaticWebTest):
    def to_test_etypes(self):
        return set(('Masters', 'Technology', 'Talk', 'Folder', 'CWUser'))

    def list_startup_views(self):
        return ('index',)


if __name__ == '__main__':
    unittest.main()
