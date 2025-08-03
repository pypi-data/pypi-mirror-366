from setuptools import setup, find_packages

setup(
    name='friendlyetl',
    version='1.0.2',
    author='Divith Raju',
    author_email='divithraju@gmail.com',
    description='A simple and lightweight ETL package for data pipelines',
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
