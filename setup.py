import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


# Package meta-data.
NAME = 'amltoolz'
DESCRIPTION = 'A library to enhance the use of Azure Machine Learning'
URL = ''
EMAIL = 'msalvaris@users.noreply.github.com'
AUTHOR = 'Mathew Salvaris'
LICENSE = ''
LONG_DESCRIPTION = DESCRIPTION


with open('requirements.txt') as f:
    requirements = f.read().splitlines()


here = os.path.abspath(os.path.dirname(__file__))

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), about)


setup(
    name=NAME,
    version=about['__version__'],
    url=URL,
    license=LICENSE,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    scripts=[],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Intended Audience :: Data Scientists & Developers',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
    ]
)
