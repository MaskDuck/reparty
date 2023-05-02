from setuptools import setup

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Developers",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]
packages = [
    "reparty",
    "reparty.core"
]
setup(
    name="reparty",
    version="0.0.1",
    description="The simple, elegant and modern way to make Discord bots",  # noqa: E501
    long_description="# hello world",
    url="",
    author="MaskDuck",
    license="MIT",
    classifiers=classifiers,
    keywords="discord",
    packages=packages,
    long_description_content_type="text/markdown",
    install_requires=[],
)
