import os
import setuptools


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        content = f.read()
    return content


setuptools.setup(
    name="pymetacode",
    version=read("VERSION").strip(),
    description="A Python package helping to write and maintain Python "
    "packages.",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    author="Till Biskup",
    author_email="till@till-biskup.de",
    url="https://www.meta-co.de/",
    project_urls={
        "Documentation": "https://python.docs.meta-co.de/",
        "Source": "https://github.com/tillbiskup/pymetacode",
    },
    packages=setuptools.find_packages(exclude=("tests", "docs")),
    license="BSD",
    keywords=[
        "metaprogramming",
        "Python packages",
        "automation",
        "code generation",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
        "Development Status :: 5 - Production/Stable",
    ],
    install_requires=[
        "jinja2",
        "pyyaml",
        "platformdirs",
    ],
    extras_require={
        "dev": [
            "prospector",
            "pyroma",
            "bandit",
            "black",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "sphinx-multiversion",
        ],
        "deployment": [
            "build",
            "twine",
        ],
    },
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "pymeta = pymetacode.cli:cli",
        ],
    },
    include_package_data=True,
)
