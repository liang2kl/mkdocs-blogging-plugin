from setuptools import find_packages, setup

file = open("README.md", "r")
LONG_DESCRIPTION = file.read()
file.close()

file = open("requirements.txt", "r")
DEPENDENCIES = file.readlines()
file.close()

del file

setup(
    name="mkdocs-blogging-plugin",
    version="1.4.0",
    description="Mkdocs plugin that generates a blog index page sorted by creation date.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    keywords="mkdocs blog plugin",
    project_urls={
        "Source": "https://github.com/liang2kl/mkdocs-blogging-plugin"
    },
    author="Liang Yesheang",
    author_email="liang2kl@outlook.com",
    include_package_data=True,
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=DEPENDENCIES,
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "blogging = mkdocs_blogging_plugin.plugin:BloggingPlugin"
        ]
    }
)
