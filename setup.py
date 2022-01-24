"""Setup script."""

from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name='flashing_tools',
    version='0.1',
    packages=find_packages(exclude=['tests']),

    install_requires=['numpy', 'PyYAML', 'PyQt6', 'pypot'],

    extra_requires={
        'test': ['pytest'],
    },

    author='Pollen Robotics',
    author_email='contact@pollen-robotics.com',
    url='https://github.com/pollen-robotics/flasing_tools',

    description="Python GUI inerfaces to flash Reachy's motors and modules.",
    # long_description=long_description,
    # long_description_content_type='text/markdown',
)