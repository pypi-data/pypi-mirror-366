import codecs
import os

from setuptools import find_packages, setup




VERSION = '1.0.0'
DESCRIPTION = 'Spider系列必备的工具包!'
LONG_DESCRIPTION = 'Spider系列必备的工具包 没有在除window系统下的其它子系统测试过,无法确认情况'

# Setting up
setup(
    name="BloodSpiderModel",
    version=VERSION,
    author="BloodSpider",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        'getch; platform_system=="Unix"',
        'getch; platform_system=="MacOS"',
    ],
    keywords=['python', 'bloodspider', 'spider', 'windows', 'mac', 'linux'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)