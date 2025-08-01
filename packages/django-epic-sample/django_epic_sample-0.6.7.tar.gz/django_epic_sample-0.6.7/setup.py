import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-epic-sample',
    version='0.6.7',
    packages=find_packages(),
    install_requires=[
        'crispy-bootstrap3',
        'django-epic[server]>=0.6.7',
    ],
    include_package_data=True,
    entry_points= {
        'console_scripts': [
            'epic-sample-bom = epic_sample.scripts.epic_bom:main',
            'epic-sample-footprints = epic_sample.scripts.epic_footprints:main'
        ]
    },
    license='MIT License',  # example license
    description='A minimal Django project to demonstrate EPIC functionality.',
    long_description=README,
    url='https://bitbucket.org/egauge/epic-sample/',
    author='David Mosberger-Tang',
    author_email='davidm@egauge.net',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
    ],
)
