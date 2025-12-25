#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for MCP Investment Portfolio. 
"""
from setuptools import setup, find_packages
import os

# 读取 README.md 作为长描述
def read_readme():
    readme_path = os. path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# 读取 requirements.txt
def read_requirements():
    req_path = os. path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='mcp-investment-portfolio',
    version='0.1.0',
    description='A Model Context Protocol (MCP) server for managing investment portfolios',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='repeaterI',
    author_email='',
    url='https://github.com/repeaterI/MCP_InvestmentPortfolio',
    license='MIT',
    
    # 包发现配置
    packages=find_packages(exclude=['tests', 'tests.*', 'docs']),
    
    # Python 版本要求
    python_requires='>=3.8',
    
    # 依赖项
    install_requires=read_requirements(),
    
    # 开发依赖
    extras_require={
        'dev':  [
            'flake8>=6.0.0',
            'pylint>=2.17.0',
            'black>=23.0.0',
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ],
        'lint': [
            'flake8>=6.0.0',
            'pylint>=2.17.0',
        ],
    },
    
    # 包含非 Python 文件
    include_package_data=True,
    package_data={
        'portfolio_server':  ['data/*.json', 'resources/*.json'],
    },
    
    # 入口点
    entry_points={
        'console_scripts':  [
            'portfolio-server=main:main',
            'claude-server=claude_server:main',
        ],
    },
    
    # 分类信息
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License ::  OSI Approved ::  MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language ::  Python :: 3.8',
        'Programming Language :: Python ::  3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Office/Business :: Financial ::  Investment',
    ],
    
    # 关键词
    keywords='mcp investment portfolio finance',
)