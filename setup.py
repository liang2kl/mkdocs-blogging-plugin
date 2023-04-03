from setuptools import find_packages, setup

with open("README.md", "r") as file:
    LONG_DESCRIPTION = file.read()

with open("requirements.txt", "r") as file:
    DEPENDENCIES = file.readlines()

setup(
    name="mkdocs-blogging-plugin",
    version="2.2.3",
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
