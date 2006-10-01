from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase

DEPENDENCIES = ['Archetypes']
PRODUCT_DEPENDENCIES = ['MimetypesRegistry', 'PortalTransforms']

# Install all (product-) dependencies, install them too
for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
    ZopeTestCase.installProduct(dependency)

PRODUCTS = list()
PRODUCTS += DEPENDENCIES

PloneTestCase.setupPloneSite(products=PRODUCTS)

from Products.Five import zcml

import Products.Five
zcml.load_config('meta.zcml', Products.Five)
zcml.load_config('permissions.zcml', Products.Five)
zcml.load_config('configure.zcml', Products.Five)
import p4a.calendar
zcml.load_config('configure.zcml', p4a.calendar)
import p4a.plonecalendar
zcml.load_config('configure.zcml', p4a.plonecalendar)

def test_suite():
    from unittest import TestSuite, makeSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite
    
    suite = TestSuite()
    suite.addTest(ZopeDocFileSuite(
        'calendar.txt',
        package='p4a.plonecalendar',
        test_class=PloneTestCase.PloneTestCase,
        )
    )

    return suite
