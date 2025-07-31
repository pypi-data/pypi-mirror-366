import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "spensireli.advanced-cdk-constructs",
    "version": "0.0.10",
    "description": "advanced-cdk-constructs",
    "license": "Apache-2.0",
    "url": "https://github.com/spensireli/advanced-cdk-constructs.git",
    "long_description_content_type": "text/markdown",
    "author": "spensireli<5614310+spensireli@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/spensireli/advanced-cdk-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "spensireli.advanced_cdk_constructs",
        "spensireli.advanced_cdk_constructs._jsii"
    ],
    "package_data": {
        "spensireli.advanced_cdk_constructs._jsii": [
            "advanced-cdk-constructs@0.0.10.jsii.tgz"
        ],
        "spensireli.advanced_cdk_constructs": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.112.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
