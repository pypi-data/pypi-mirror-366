from setuptools import setup, find_packages

setup(
    name="run_vast",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "vast_api",
        "coloredlogs",
        "pandas",
    ],
    entry_points={
        'console_scripts': [
            'run_vast=run_vast.run_vast:main',
            'rv=run_vast.run_vast:main',
        ],
    },
    author="Andrew Healey",
    author_email="doolie.healey@gmail.com",
    description="A tool for running commands on vast.ai instances",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/andrew-healey/run_vast",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 