from distutils.core import setup
import setuptools
setup(
  name = 'targa',
  packages = ['targa', 'targa.errors'],
  version = '1.0.2',
  license='MIT',
  description = 'A lightweight async Python library for MySQL queries and modeling.',
  author = 'whdev1',
  author_email = 'whdev1@protonmail.com',
  url = 'https://github.com/whdev1/targa',
  download_url = 'https://github.com/whdev1/targa/archive/refs/tags/v1.0.2.tar.gz',
  keywords = ['Targa', 'SQL', 'MySQL', 'async'],
  install_requires=['aiomysql'],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10'
  ],
)