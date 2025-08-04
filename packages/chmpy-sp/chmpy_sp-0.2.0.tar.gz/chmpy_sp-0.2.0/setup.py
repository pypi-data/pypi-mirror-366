from setuptools import setup, find_packages

setup(
    name='chmpy-sp',
    license="MIT",
    version='0.2.0',
    include_package_data=True,
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