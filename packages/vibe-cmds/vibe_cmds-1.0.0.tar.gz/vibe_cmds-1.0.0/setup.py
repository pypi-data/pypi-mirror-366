from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vibe-cmds",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "gitpython>=3.1.0",
        "pillow==11.3.0",
    ],
    entry_points={
        "console_scripts": [
            "ass=vibe_cmds.ass:ass_command",
            "css=vibe_cmds.css:css_command",
            "dss=vibe_cmds.dss:dss_command",
            "fss=vibe_cmds.fss:fss_command",
        ],
    },
    author="monosolo101",
    author_email="monosolo1on1@gmail.com",
    description="Useful vibe coding cli commands.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="git, utility, commands",
    python_requires=">=3.6",
    zip_safe=False,
    include_package_data=True,
)
