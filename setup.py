import os

from setuptools import find_packages, setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()


setup(
    name='bai-lockbox',
    version='0.0.4',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'six',
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'coverage'],
    include_package_data=True,
    license='Apache License 2.0',
    description='A library for parsing files in the BAI lockbox format.',
    long_description=README,
    url='https://www.github.com/FundersClub/bai-lockbox',
    author='Jon Friedman / FundersClub Inc.',
    author_email='jon@fundersclub.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry'
    ],
)
