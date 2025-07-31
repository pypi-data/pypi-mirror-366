from setuptools import setup, find_packages

setup(
    name='max_min_by_sg',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    description='Maxima/Minima solver using C++ and Python integration',
    python_requires='>=3.6',
)
