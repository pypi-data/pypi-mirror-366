#!/usr/bin/env python

"""
distutils/setuptools install script.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import re

sdk_version = ''
with open('ks3/__init__.py', 'r') as fd:
    sdk_version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)


with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='ks3sdk',
    version=sdk_version,
    description='Ksyun KS3 SDK',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=['ks3', 'ks3.xmlParsers'],
    install_requires=[
        'six', 'python-dateutil',
        'aiofiles~=23.2.1',
        'crcmod~=1.7',
        'pycryptodome~=3.20.0',
        'requests',
    ],
    include_package_data=True,
    url='https://gitee.com/ks3sdk/ks3-python-sdk',
    author='ksc_ks3',
    author_email='ksc_ks3@kingsoft.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    python_requires='>=3.6'
)
