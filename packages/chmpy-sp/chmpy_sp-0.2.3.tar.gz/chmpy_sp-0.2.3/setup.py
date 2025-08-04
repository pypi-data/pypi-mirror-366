from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
setup(
    name='chmpy-sp',
    license="MIT",
    version='0.2.3',
    author="Ammar Syamil",
    author_email="ammarsyamil057@gmail.com",
    include_package_data=True,
    long_description=long_description,
    description="python TUI for chaning file/folder permission",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'textual>=0.74.0', 
        'art'
    ],
    entry_points={
        "console_scripts": [
            "chmpy-sp = chmpy.main:main",  
        ],
    },
)