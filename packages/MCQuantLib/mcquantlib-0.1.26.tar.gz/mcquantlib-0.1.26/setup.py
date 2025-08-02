#!/usr/bin/python
#coding = utf-8

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MCQuantLib",
    version="0.1.26",
    author="Syuya_Murakami",
    author_email="wxy135@mail.ustc.edu.cn",
    description="MCQuantLib is a QuantLib derivative to perform Monte Carlo pricing of options.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://mcquantlib-doc.readthedocs.io/en/latest/index.html",
    project_urls={
        "Bug Tracker": "https://github.com/SyuyaMurakami/MCQuantLib",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=['numpy','pandas','QuantLib','joblib']
)
