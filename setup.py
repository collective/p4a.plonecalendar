from setuptools import setup, find_packages
import sys, os

version = '1.1'

setup(name='p4a.plonecalendar',
      version=version,
      description="Plone4Artists calendar add-on for Plone",
      long_description="""p4a.plonecalendar is a calendaring add-on for the
Plone CMS.""",
      classifiers=[
          'Framework :: Zope3',
          'Framework :: Plone',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='Plone4Artists ',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://www.plone4artists.org/products/plone4artistscalendar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.calendar==1.1',
          'p4a.subtyper>=1.0.1',
          'p4a.common>=1.0.1',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
