import os
import os.path
import sys
import subprocess

from setuptools import setup, Extension
import versioneer

# Default description in markdown
long_description = open('README.md').read()
   

PKG_NAME     = 'calas7262'
AUTHOR       = 'Rafael Gonzalez'
AUTHOR_EMAIL = 'astrorafael@gmail.com'
DESCRIPTION  = 'Utility to calibrate AS7262 spectral photometers',
LICENSE      = 'MIT'
KEYWORDS     = 'Astronomy Python RaspberryPi'
URL          = 'http://github.com/astrorafael/calas7262/'
PACKAGES     = ["calas7262","calas7262.service"]
DEPENDENCIES = [
                  'pyserial',
                  'twisted >= 16.3.0',
                  'tabulate'
                ]

if sys.version_info[0] == 2:
  DEPENDENCIES.append('statistics')

CLASSIFIERS  = [
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Windows',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering :: Astronomy',
    'Topic :: Scientific/Engineering :: Atmospheric Science',
    'Development Status :: 4 - Beta',
]


DATA_FILES  = [ 
    ('/usr/local/bin',   ['files/usr/local/bin/calas7262']),
]

# Additional data inside the package
PACKAGE_DATA = {
    'calas7262': ['data/QE_photodiode.csv'],
}
                                
setup(name             = PKG_NAME,
      version          = versioneer.get_version(),
      cmdclass         = versioneer.get_cmdclass(),
      author           = AUTHOR,
      author_email     = AUTHOR_EMAIL,
      description      = DESCRIPTION,
      long_description = long_description,
      license          = LICENSE,
      keywords         = KEYWORDS,
      url              = URL,
      classifiers      = CLASSIFIERS,
      packages         = PACKAGES,
      install_requires = DEPENDENCIES,
      data_files       = DATA_FILES,
      package_data     = PACKAGE_DATA
      )
