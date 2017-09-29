from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open( path.join(path.abspath(path.dirname(__file__)) , 'README.md' )) as f:
    long_description = f.read()

setup(
    name = 'restam',
    version = '0.0.04',
    packages = ["restam"],
    scripts=['restam/__main__.py'],
    #entry_points = {
    #    'console_scripts': ['vernam = vernam.__main__:main']
    #},

    description = 'Vernam cipher',
    long_description = long_description,

    url = 'https://github.com/roysoup/Restam',

    author = 'Roy Siu',
    author_email = '',

    license = 'MIT Licence',

    classifiers = [
        'Development Status :: 0 - In Development'
    ],
    
    install_requires = ['typing'],
)