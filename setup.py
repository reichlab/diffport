from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

project_url = "https://github.com/reichlab/diffport"

setup(
    name="diffport",
    version="0.4.0",
    description="Database summary diff reporting tool",
    long_description=readme,
    author="Abhinav Tushar",
    author_email="lepisma@fastmail.com",
    url=project_url,
    install_requires=[
        "pydash",
        "colorama",
        "docopt",
        "dataset",
        "jinja2",
        "pyyaml",
        "tabulate",
        "psycopg2"
    ],
    setup_requires=[
        "pytest-runner"
    ],
    tests_require=[
        "pytest"
    ],
    keywords="",
    packages=find_packages(),
    entry_points={"console_scripts": ["diffport=diffport.cli:main"]},
    classifiers=(
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only"
    ))
