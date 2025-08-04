from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shooortcuts",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "gitpython>=3.1.0",
        "pillow==11.3.0",
    ],
    entry_points={
        "console_scripts": [
            "rsimg=shooortcuts.rsimg:rsimg_command",
        ],
    },
    author="monosolo101",
    author_email="monosolo1on1@gmail.com",
    description="Simple and helpful cli shortcuts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="git, utility, commands",
    python_requires=">=3.6",
    zip_safe=False,
    include_package_data=True,
)
