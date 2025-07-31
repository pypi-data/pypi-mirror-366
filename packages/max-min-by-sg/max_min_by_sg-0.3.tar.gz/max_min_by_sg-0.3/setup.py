from setuptools import setup, find_packages

setup(
    name='max_min_by_sg',
    version='0.3',  
    packages=find_packages(),
    include_package_data=True,
    description='Maxima/Minima solver using C logic rewritten in Python',
    python_requires='>=3.6',
)
