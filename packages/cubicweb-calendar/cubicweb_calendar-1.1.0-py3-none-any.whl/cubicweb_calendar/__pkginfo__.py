# pylint: disable-msg=W0622
"""cubicweb-calendar application packaging information"""

modname = 'calendar'
distname = 'cubicweb-calendar'

numversion = (1, 1, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
description = 'calendar component for the CubicWeb framework'
author = 'Logilab'
author_email = 'contact@logilab.fr'
web = 'http://www.cubicweb.org/project/%s' % distname
classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends__ = {'cubicweb': ">=4.10.0,<6.0.0", 'cubicweb-web': ">=1.6.0,<2.0.0"}
