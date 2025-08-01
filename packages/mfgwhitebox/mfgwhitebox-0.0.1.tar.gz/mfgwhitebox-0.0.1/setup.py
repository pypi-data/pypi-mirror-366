
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mfgwhitebox",
    version="0.0.1",
    author="liumao0917",
    author_email="liumao0917@gmail.com",
    description="A package to convert between Excel and XML files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hedaima/excel-xml-converter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'openpyxl',
        'lxml',
    ],
    entry_points={
        'console_scripts': [
            'mfgwhitebox=mfgwhitebox.converter:main',
        ],
    },
)
