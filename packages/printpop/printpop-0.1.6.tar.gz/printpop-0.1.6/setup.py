from setuptools import setup, find_packages

setup(
    name="printpop",
    version="0.1.6",
    packages=find_packages(),  # This auto-discovers the 'printpop' folder
    include_package_data=True,
)