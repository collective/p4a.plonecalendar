from setuptools import setup, find_packages

version = '2.1b2.dev0'

f = open('README.rst')
readme = f.read()
f.close()

f = open('CHANGES.txt')
changes = f.read()
f.close()


setup(name='p4a.plonecalendar',
      version=version,
      description="Plone4Artists calendar add-on for Plone",
      long_description=readme + '\n\n' + changes,
      classifiers=[
          'Framework :: Zope2',
          'Framework :: Plone',
	  'Framework :: Plone :: 4.0',
          'Framework :: Plone :: 4.1',
          'Framework :: Plone :: 4.2',
          'Framework :: Plone :: 4.3',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='Plone4Artists events event calendar calendaring',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://github.com/collective/p4a.plonecalendar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plone.memoize',
          'dateable.chronos',
          'dateable.kalends',
          'p4a.common >= 1.0.1',
          'p4a.z2utils >= 1.0',
      ],
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,      
      )
