[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mcp-investment-portfolio"
version = "0.1.0"
description = "A Model Context Protocol (MCP) server for managing investment portfolios"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.8"
authors = [
    {name = "repeaterI"}
]
keywords = ["mcp", "investment", "portfolio", "finance"]
classifiers = [
    "Development Status ::  3 - Alpha",
    "Intended Audience ::  Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language ::  Python :: 3.9",
    "Programming Language :: Python ::  3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Office/Business ::  Financial :: Investment",
]
dependencies = [
    "mcp[cli]>=1.5.0",
    "pandas>=2.0.0",
    "httpx>=0.25.0",
    "matplotlib>=3.7.0",
    "uvicorn>=0.25.0",
    "starlette>=0.36.0",
]

[project.optional-dependencies]
dev = [
    "flake8>=6.0.0",
    "pylint>=2.17.0",
    "black>=23.0.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]
lint = [
    "flake8>=6.0.0",
    "pylint>=2.17.0",
]

[project. scripts]
portfolio-server = "main:main"
claude-server = "claude_server:main"

[project.urls]
Homepage = "https://github.com/repeaterI/MCP_InvestmentPortfolio"
Repository = "https://github.com/repeaterI/MCP_InvestmentPortfolio"

[tool. setuptools]
packages = ["portfolio_server", "portfolio_server. api", "portfolio_server. data", "portfolio_server. resources", "portfolio_server. tools"]

[tool.setuptools.package-data]
portfolio_server = ["data/*.json", "resources/*.json"]

# 代码检查配置
[tool. flake8]
max-line-length = 120
exclude = [". git", "__pycache__", "build", "dist", "*. egg-info", ".venv", "venv"]
ignore = ["E501", "W503"]

[tool.pylint. messages_control]
disable = ["C0114", "C0115", "C0116", "R0903", "W0612"]
max-line-length = 120

[tool.pylint.format]
max-line-length = 120

[tool.black]
line-length = 120
target-version = ["py38", "py39", "py310", "py311", "py312"]
exclude = '''
/(
    \.git
  | __pycache__
  | build
  | dist
  | \.venv
  | venv
)/
'''

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*. py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"