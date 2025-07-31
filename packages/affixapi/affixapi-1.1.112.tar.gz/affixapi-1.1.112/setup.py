
## ->  https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

## -> generated (previously)
from setuptools import setup, find_packages  # noqa: H301

NAME = "affixapi"
VERSION = "1.1.112"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
  "urllib3 >= 1.25.3",
  "python-dateutil",
]

setup(
    name=NAME,
    version=VERSION,
    description="Affix API",
    author="OpenAPI Generator community",
    author_email="developers@affixapi.com",
    url="",
    keywords=["OpenAPI", "OpenAPI-Generator", "Affix API"],
    python_requires=">=3.6",
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
