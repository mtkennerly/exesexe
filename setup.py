
from setuptools import setup

with open("README.md") as file:
    long_description = file.read()

setup(
    name="exesexe",
    version="1.0.0",
    description="Manipulate return codes from executables",
    long_description=long_description,
    url="https://github.com/mtkennerly/exesexe",
    author="Matthew T. Kennerly (mtkennerly)",
    author_email="mtkennerly@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities"
    ],
    keywords="return code",
    py_modules=["exesexe"],
    extras_require={
        "dev": [
            "invoke",
            "pyinstaller",
            "tox"
        ]
    },
    entry_points={
        "console_scripts": [
            "exesexe=exesexe:main",
        ],
    }
)
