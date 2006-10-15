from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import layer

DEPENDENCIES = ['Archetypes']
PRODUCT_DEPENDENCIES = ['MimetypesRegistry', 'PortalTransforms']

# Install all (product-) dependencies, install them too
for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
    ZopeTestCase.installProduct(dependency)

PRODUCTS = list()
PRODUCTS += DEPENDENCIES

PloneTestCase.setupPloneSite(products=PRODUCTS)

from Products.Five import zcml
import p4a.calendar
import p4a.plonecalendar

class AudioTestCase(PloneTestCase.PloneTestCase):
    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        zcml.load_config('configure.zcml', p4a.calendar)
        zcml.load_config('configure.zcml', p4a.plonecalendar)

def test_suite():
    from unittest import TestSuite, makeSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite
    
    suite = TestSuite()
    suite.addTest(ZopeDocFileSuite(
        'calendar.txt',
        package='p4a.plonecalendar',
        test_class=AudioTestCase,
        )
    )

    suite.layer = layer.ZCMLLayer

    return suite
