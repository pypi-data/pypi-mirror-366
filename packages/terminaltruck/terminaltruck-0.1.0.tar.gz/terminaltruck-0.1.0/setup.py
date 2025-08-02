from setuptools import setup, find_packages

setup(
    name="terminaltruck",
    version="0.1.0",
    author="Vitek",
    author_email="cheeseqwertycheese@gmail.com",
    description="Game about trucking",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Viktor640266/driver",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    packages = find_packages(),
    entry_points={
        'console_scripts': ['truck = game:main']
    })