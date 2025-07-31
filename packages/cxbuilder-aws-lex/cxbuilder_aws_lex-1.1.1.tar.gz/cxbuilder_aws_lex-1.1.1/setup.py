import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cxbuilder-aws-lex",
    "version": "1.1.1",
    "description": "Higher-level (L2) constructs for AWS LexV2 bot creation using the AWS CDK",
    "license": "MIT",
    "url": "https://github.com/cxbuilder/aws-lex#readme",
    "long_description_content_type": "text/markdown",
    "author": "CXBuilder<ivan@cxbuilder.ai>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cxbuilder/aws-lex.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cxbuilder_aws_lex",
        "cxbuilder_aws_lex._jsii"
    ],
    "package_data": {
        "cxbuilder_aws_lex._jsii": [
            "aws-lex@1.1.1.jsii.tgz"
        ],
        "cxbuilder_aws_lex": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib==2.194.0",
        "constructs>=10.0.0, <11.0.0",
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
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved",
        "Framework :: AWS CDK",
        "Framework :: AWS CDK :: 2"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
