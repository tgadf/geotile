from distutils.core import setup
import setuptools

setup(
  name = 'geotile',
  py_modules = ['geotile'],
  version = '0.0.1',
  description = 'A Python Geotiling Tool',
  long_description = open('README.md').read(),
  author = 'Thomas Gadfort',
  author_email = 'tgadfort@gmail.com',
  license = "MIT",
  url = 'https://github.com/tgadf/geotile',
  keywords = ['geohash', 'location'],
  classifiers = [
    'Development Status :: 3',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ]
)
 
