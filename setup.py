from setuptools import setup, find_packages

version = '2.1b2.dev0'

f = open('README.txt')
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
          'Framework :: Zope3',
          'Framework :: Plone',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='Plone4Artists events event calendar calendaring',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://svn.plone.org/svn/collective/p4a/p4a.plonecalendar/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          'plone.memoize',
          'dateable.chronos',
          'dateable.kalends',
          'p4a.calendar >= 1.2dev',
      ],
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,      
      )
