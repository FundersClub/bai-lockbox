import os

from setuptools import find_packages, setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='bai-lockbox',
    version='0.0.1',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'django-jsonfield>=0.8.11',
        'six',
        'django-apptemplates',
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'coverage'],
    include_package_data=True,
    license='LGPLv3',
    description='An elegant solution for keeping a relational log of chronological events in a Django application.',
    url='https://www.github.com/FundersClub/bai-lockbox',
    author='Jon Friedman / FundersClub Inc.',
    author_email='jon@fundersclub.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Intended Audience :: Developers',
    'Intended Audience :: Financial and Insurance Industry'
    ],
)
