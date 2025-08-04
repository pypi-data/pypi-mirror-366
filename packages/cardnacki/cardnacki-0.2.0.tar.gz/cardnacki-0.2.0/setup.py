from setuptools import find_packages, setup

with open("src/README.md", "r") as f:
    long_description = f.read()

setup(
    name="cardnacki",
    version="0.2.0",
    description="A playing cards package",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bernackimark/cardnacki",
    author="Bernacki",
    author_email="bernackimark@gmail.com",
    extras_require={"dev": "twine>=4.0.2"},
    python_requires=">=3.10",
)
