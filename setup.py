#!/usr/bin/env python
import os

import sys
from setuptools import find_packages, setup


def read_requirements(txt='requirements.txt'):
    folder = os.path.dirname(os.path.realpath(__file__))
    path = folder + "/" + txt
    requirements = []
    if os.path.isfile(path):
        with open(path) as f:
            requirements = f.read().splitlines()
    return requirements


if __name__ == '__main__':
    print("Out %s" % " ".join(sys.argv))
    setup(
        name='lpass-ssh',
        version='1.0.0',
        packages=find_packages(include=["lpassssh", "lpassssh.*"]),
        entry_points={
            'console_scripts': [
                'lpass-ssh = lpassssh.__main__:startup'
            ]
        },
        install_requires=read_requirements(),
        extras_require={'dev': (read_requirements("dev.requirements.txt"))}
    )
