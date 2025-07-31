#!/user/bin/env python

import re, uuid
from setuptools import setup, find_packages
import io

with io.open("genderator/__init__.py", "r", encoding="utf-8") as f:
    init_content = f.read()

match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", init_content, re.M)

if not match:
    raise RuntimeError("Could not find __version__ in genderator/__init__.py")

version = match.group(1)


with open("README.rst", "r", encoding='utf-8') as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    install_reqs = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(name='genderator311',
      version=version,
      description='Python library to guess gender given a spanish full name for Python 3.11+',
      long_description=long_description,
      author='David Moreno-Garcia (mantained by Diego Delgado)',
      author_email='ddelgado.1405@gmail.com',
      license='MIT',
      url='https://github.com/xumixprto/genderator311',
      download_url=f"https://github.com/xumixprto/genderator311/archive/refs/tags/v{version}.tar.gz",
      keywords=['gender', 'guess', 'spanish', 'name'],
      packages=find_packages(exclude=['tests']),
      install_requires=install_reqs,
      include_package_data=True,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Topic :: Software Development :: Libraries',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
      ]
      )
