from setuptools import setup, find_packages

setup(
    name='friendlyetl',
    version='1.0.0',
    author='Divith Raju',
    author_email='divithraju@gmail.com',
    description='A user-friendly Python ETL package for transforming CSV data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://www.linkedin.com/in/divithraju',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'pandas',
        'openpyxl'
    ],
    python_requires='>=3.6',
)
