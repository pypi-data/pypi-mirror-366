"""
Setup configuration for PAB - APCloudy Deployment Tool
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from version.py
version = {}
with open(os.path.join(this_directory, 'pab_cli', 'version.py')) as f:
    exec(f.read(), version)

setup(
    name='pab-cli',
    version=version['__version__'],
    author='Fawad Ali',
    author_email='Fawadstar6@gmail.com',
    description='APCloudy Deployment Tool for Scrapy Spiders',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fawadss1/pab-cli',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Distributed Computing',
    ],
    python_requires='>=3.8',
    install_requires=[
        'click>=8.2.1',
        'requests>=2.32.4',
        'colorama>=0.4.6',
    ],
    entry_points={
        'console_scripts': [
            'pab=pab_cli.cli:main',
        ],
    },
    keywords='scrapy deployment apcloudy spider automation',
    project_urls={
        'Bug Reports': 'https://github.com/fawadss1/pab-cli/issues',
        'Source': 'https://github.com/fawadss1/pab-cli',
        'Documentation': 'https://github.com/fawadss1/pab-cli#readme',
    },
)
