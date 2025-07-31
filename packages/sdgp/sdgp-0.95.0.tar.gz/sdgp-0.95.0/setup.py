from setuptools import setup, find_packages

setup(
    name='sdgp',
    version='0.95.0',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'my_command = sdgp.module:main_func',
        ],
    },
    # ... 他のメタデータ ...
)
