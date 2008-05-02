from unittest import TestSuite
from zope.testing import doctest
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer

PloneTestCase.setupPloneSite()        

def test_suite():

    suite = TestSuite()
    suite.addTest(doctest.DocTestSuite('p4a.plonecalendar.sitesetup',
                                       optionflags=doctest.ELLIPSIS))
    # XXX these re browser tests, mostly, and should be moved to chronos.
    #suite.addTest(ZopeDocFileSuite('calendar.txt',
                                   #package='p4a.plonecalendar',
                                   #test_class=CalendarTestCase,))
    suite.layer = layer.ZCMLLayer

    return suite
