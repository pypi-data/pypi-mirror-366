from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shooortcuts",
    version="0.3.2",
    packages=find_packages(),
    install_requires=[
        "gitpython>=3.1.0",
        "pillow==11.3.0",
    ],
    entry_points={
        "console_scripts": [
            "ass=shooortcuts.ass:ass_command",
            "css=shooortcuts.css:css_command",
            "dss=shooortcuts.dss:dss_command",
            "fss=shooortcuts.fss:fss_command",
            "rsimg=shooortcuts.rsimg:rsimg_command",
        ],
    },
    author="imhuwq",
    author_email="imhuwq@gmail.com",
    description="Helpful Git shortcuts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="git, utility, commands",
    python_requires=">=3.6",
    zip_safe=False,
    include_package_data=True,
)
