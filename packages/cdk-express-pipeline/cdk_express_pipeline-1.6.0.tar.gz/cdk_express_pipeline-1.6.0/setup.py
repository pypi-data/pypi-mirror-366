import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk_express_pipeline",
    "version": "1.6.0",
    "description": "CDK pipelines provides constructs for Waves, Stages using only native CDK stack dependencies",
    "license": "Apache-2.0",
    "url": "https://github.com/rehanvdm/cdk-express-pipeline.git",
    "long_description_content_type": "text/markdown",
    "author": "rehanvdm<rehan.vdm4+github@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/rehanvdm/cdk-express-pipeline.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_express_pipeline",
        "cdk_express_pipeline._jsii"
    ],
    "package_data": {
        "cdk_express_pipeline._jsii": [
            "cdk-express-pipeline@1.6.0.jsii.tgz"
        ],
        "cdk_express_pipeline": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.133.0, <3.0.0",
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
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
