from setuptools import setup, find_packages

# Read README.md content
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="friendlyetl",
    version="1.0.1",
    author="Divith Raju",
    author_email="youremail@example.com",
    description="A beginner-friendly Python ETL package for CSV, Excel, JSON, and MySQL workflows.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Important!
    url="https://github.com/divithraju/",  # Optional
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=[
        "pandas",
        "sqlalchemy",
        "mysql-connector-python",
    ],
)
