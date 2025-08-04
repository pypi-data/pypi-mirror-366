# -*- coding: utf-8 -*-
'''
@time: 2025/8/4 11:48
@ author: hxp
'''
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="current-controller-api",  # 包名称（pip安装时的名称）
    version="1.0.0",  # 版本号
    author="hxp",
    author_email="rongaluo@163.com",  # 可替换为实际邮箱
    description="电流控制器串口通信SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/yourusername/current-controller-sdk",  # 可替换为代码仓库地址
    packages=find_packages(),  # 自动发现包目录
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,  # 依赖清单
)