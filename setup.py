from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as req:
        return req.read().strip().split('\n')

setup(
    name='pyxplore',
    version='0.1.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyxplore=pyxplore.pyxplore:main',  # "main" should be your main function in pyxplore.py
        ],
    },
    install_requires=read_requirements(),
)
