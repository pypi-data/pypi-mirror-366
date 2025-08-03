import os
import setuptools


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        content = file.read()
    return content


setuptools.setup(
    name="qtbricks",
    version=read("VERSION").strip(),
    description="Python Qt components: widgets and utils, focussing on "
    "scientific GUIs",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    author="Till Biskup",
    author_email="code@till-biskup.de",
    url="https://pypi.org/project/qtbricks/",
    project_urls={
        "Documentation": "https://qtbricks.docs.till-biskup.de/",
        "Source": "https://github.com/tillbiskup/qtbricks",
    },
    packages=setuptools.find_packages(exclude=("tests", "docs")),
    license="BSD",
    keywords=[
        "Qt",
        "widgets",
        "building blocks",
        "PySide6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development",
        "Development Status :: 4 - Beta",
    ],
    install_requires=[
        "PySide6",
        "matplotlib",
    ],
    extras_require={
        "dev": [
            "prospector",
            "pyroma",
            "bandit",
            "black",
            "pymetacode",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "sphinx_multiversion",
        ],
        "deployment": [
            "build",
            "twine",
        ],
    },
    python_requires=">=3.9",
    include_package_data=True,
)
