from setuptools import setup, find_packages
import os, io, re

NAME = "tencentcloud-dlc-sqlalchemy"
DESCRIPTION = "Tencentcloud DLC SQLAlchemy, using DLC dialect ."
LICENCE = "Apache License Version 2.0"
AUTHOR = "Tencentcloud DLC Team."
MAINTAINER_EMAIL = "valuxzhao@tencent.com"
URL = "https://cloud.tencent.com/product/dlc"
DOWNLOAD_URL = "https://cloud.tencent.com/product/dlc"
PLATFORMS='any'



def read(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()

def version(path):
    
    version_file = read(path)
    version_match = re.search(
        r"""^VERSION = ['"]([^'"]*)['"]""", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


VERSION = version("tdlc_sqlalchemy/version.py")



setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    maintainer_email=MAINTAINER_EMAIL,
    packages=find_packages(exclude=["test*"]),
    platforms=PLATFORMS,
    keywords=["TencentCloud", "DLC", "sqlalchemy"],
    license=LICENCE,

    install_requires=[
        "tencentcloud-dlc-connector",
    ],
    entry_points={
        "sqlalchemy.dialects": ["dlc = tdlc_sqlalchemy:DlcDialect"]
    },
)
