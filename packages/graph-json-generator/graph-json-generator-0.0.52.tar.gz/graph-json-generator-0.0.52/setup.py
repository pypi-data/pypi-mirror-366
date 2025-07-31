from setuptools import find_packages
from setuptools import setup

setup(
    name="graph-json-generator",
    version="0.0.52",
    description="Transforming any data sources into graphs in JSON format",
    url="https://github.com/QubitPi/Antiqua/tree/master/graph-json-generator",
    author="Jiaqi Liu",
    author_email="jack20220723@gmail.com",
    license="Apache-2.0",
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=["pyyaml", "nltk"],
    zip_safe=False,
    include_package_data=True,
    setup_requires=["setuptools-pep8", "isort"],
    test_suite='tests',
)
