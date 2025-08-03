"""Setup for aryahelpers modules"""
from setuptools import setup, find_packages

BASE_REPO = 'https://gitlab.com/adhikari.ratan/generic-helpers'

setup(
    name='generichelpers',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    version='1.5',
    description='Generic Helper Modules',
    long_description='Helper Python modules for general purpose',
    author='Ratnadip Adhikari',
    author_email='ratnadip.adhikari@gmail.com',
    url=BASE_REPO + '.git',
    download_url=BASE_REPO,
    keywords=['utilities', 'python', 'helper modules'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities"
    ],
    platforms=['any'],
    install_requires=[],
    # package_data={'aryahelpers': ['configs/config.json']}
    include_package_data=True
)
