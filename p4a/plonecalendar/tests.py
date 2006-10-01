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

def testclass_builder(**kwargs):
    class PloneIntegrationTestCase(PloneTestCase.PloneTestCase):
        """Base integration TestCase for p4a.plonecalendar."""
    
        # Commented out for now, it gets blasted at the moment anyway.
        # Place it in the protected section if you need it.
        #def afterSetup(self):
        #    """
        #    """
        #    pass
    for key, value in kwargs.items():
        setattr(PloneIntegrationTestCase, key, value)
    return PloneIntegrationTestCase

def test_suite():
    from unittest import TestSuite, makeSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite
    
    suite = TestSuite()
    suite.addTest(ZopeDocFileSuite(
        'calendar.txt',
        package='p4a.plonecalendar',
        test_class=testclass_builder()
        )
    )

    return suite