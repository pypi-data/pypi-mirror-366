from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="cli_calculator",
    version="0.0.2",
    author="Robson",
    description="A simple terminal calculator supporting basic arithmetic operations.",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robson-k/cli-calculator",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={"console_scripts": ["cli_calculator = cli_calculator.main:main"]},
    license="MIT",
)
