import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="evolutionsimulator",
    version="0.1.6",
    description="Simulate evolution",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/koefoeden/Evolution-Simulator",
    author="koefoeden",
    author_email="koefoeden@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",],
    packages=["evolutionsimulator.src"],
    include_package_data=True,
    install_requires=["colorama<=0.4.3","cursor<=1.3.4", "keyboard<=0.13.4",
                      "numpy<=1.18.1", "pandas<=1.0.1", "python-dateutil<=2.8.1",
                      "pytz<=2019.3", "six<=1.14.0", "termcolor<=1.1.0",
                      "tkinterhtml<=0.7"],
    entry_points={
        "console_scripts": [
            "simulate=evolutionsimulator.__main__:main",
        ]
    },
)