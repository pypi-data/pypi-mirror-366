import os

from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="btc-version-manager",
    version="0.6.2",
    packages=["version_control"],
    include_package_data=True,
    license="BSD License",
    description="An application that adds functionality to track model object versions for any other Django application.",
    long_description=README,
    url="https://github.com/MEADez/btc-version-manager",
    author="MEADez",
    author_email="m3adez@gmail.com",
    install_requires=["psycopg2-binary>=2.9.7", "Django>=2.2.0, <=6.0.0"],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
