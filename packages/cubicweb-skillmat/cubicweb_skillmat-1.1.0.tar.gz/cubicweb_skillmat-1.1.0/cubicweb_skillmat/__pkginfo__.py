# pylint: disable-msg=W0622
"""cubicweb-skillmat application packaging information"""

modname = 'skillmat'
distname = 'cubicweb-skillmat'

numversion = (1, 1, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
description = 'skill matrix component for the CubicWeb framework'
author = 'Logilab'
author_email = 'contact@logilab.fr'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {'cubicweb': ">=4.10.0,<6.0.0",
               'cubicweb-web': ">=1.6.0,<2.0.0",
               'cubicweb-folder': ">=3.1.0,<4.0.0",
               'cubicweb-comment': ">=3.1.0,<4.0.0",
               "pandas": ">=1.5.0,<1.6.0",
               "numpy": "<2"}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]
