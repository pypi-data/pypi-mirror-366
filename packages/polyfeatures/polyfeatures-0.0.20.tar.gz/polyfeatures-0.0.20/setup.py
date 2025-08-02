from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open("C:/Reyansh/Python/Github Projects/PolyFeatures-main/README.md", encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.20'
DESCRIPTION = 'Package for featurizing polymers.'

# Setting up
setup(
    name="polyfeatures",
    version=VERSION,
    author="Reyansh Saindane",
    author_email="<reyansh.saindane@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['rdkit', 'networkx', 'joblib', 'tqdm', 'pandas', 'numpy', 'matplotlib'],
    keywords=['python'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)