#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for MCP Investment Portfolio. 
Compatible with Python 3.6+ and older setuptools versions.
"""
from setuptools import setup, find_packages
import os
import io

# 获取当前目录
here = os.path.abspath(os.path. dirname(__file__))

# 读取 README. md 作为长描述
def read_readme():
    readme_path = os. path.join(here, 'README. md')
    if os.path.exists(readme_path):
        with io. open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# 读取 requirements.txt
def read_requirements():
    req_path = os.path. join(here, 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with io. open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

# 版本号
VERSION = '0.1.0'

setup(
    name='mcp-investment-portfolio',
    version=VERSION,
    description='A Model Context Protocol (MCP) server for managing investment portfolios',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='repeaterI',
    author_email='',
    url='https://github.com/repeaterI/MCP_InvestmentPortfolio',
    license='MIT',
    
    # 包发现配置
    packages=find_packages(exclude=['tests', 'tests.*', 'docs']),
    
    # Python 版本要求 - 兼容 Python 3.6
    python_requires='>=3.6',
    
    # 依赖项
    install_requires=read_requirements(),
    
    # 开发依赖
    extras_require={
        'dev': [
            'flake8',
            'pylint',
            'pytest',
        ],
        'lint': [
            'flake8',
            'pylint',
        ],
    },
    
    # 包含非 Python 文件
    include_package_data=True,
    
    # 分类信息
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python ::  3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language ::  Python :: 3.10',
        'Programming Language :: Python ::  3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Office/Business ::  Financial ::  Investment',
    ],
    
    # 关键词
    keywords='mcp investment portfolio finance',
    
    # zip 安全标志
    zip_safe=False,
)