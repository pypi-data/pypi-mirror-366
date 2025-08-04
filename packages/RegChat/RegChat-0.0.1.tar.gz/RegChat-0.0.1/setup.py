from setuptools import Command, find_packages, setup

__lib_name__ = "RegChat"
__lib_version__ = "0.0.1"
__description__ = "Inferring intercellular and intracellular communications from single cell and spatial multi-omics data using RegChat"
__url__ = "https://github.com/lhzhanglabtools/RegChat"
__author__ = "Lihua Zhang"
__author_email__ = "zhanglh@whu.edu.cn"
__license__ = "MIT"
__keywords__ = ["cell communication", "multi-omics data", "Graph nerual network", "Contrastive learning"]
__requires__ = ["requests",]

setup(
    name = __lib_name__,
    version = __lib_version__,
    description = __description__,
    url = __url__,
    author = __author__,
    author_email = __author_email__,
    license = __license__,
    packages = ['RegChat'],
    install_requires = __requires__,
    zip_safe = False,
    include_package_data = True,
)

