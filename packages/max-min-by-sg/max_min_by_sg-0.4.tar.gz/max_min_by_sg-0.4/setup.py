from setuptools import setup, find_packages

setup(
    name="max_min_by_sg",
    version="0.4",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'max_min_by_sg': ['*.exe', '*.py', '*.txt'],
    },
    entry_points={
        'console_scripts': [
            'maxminbysg = max_min_by_sg.main:main_entry',
        ],
    },
    python_requires='>=3.6',
    description="CLI Maxima/Minima Solver using .exe and Python integration",
)
