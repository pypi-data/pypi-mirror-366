[tool.poetry]
name = "{name}-connector"
version = "0.1.0"
description = "Basic {name} connector for Agent Handler"
readme = "README.md"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = ">=3.10"
agent-handler-sdk = "^{version}"

[tool.poetry.dev-dependencies]
pytest = "^8.3.0"
pytest-cov = "^4.0.0"
pytest-asyncio = "^0.24.0"
pytest-mock = "^3.11.1"
mypy = "^1.5.1"
pre-commit = "^3.4.0"
tox = "^4.11.1"
ruff = "^0.7.4"

[build-system]
requires = ["poetry-core>=1.0.0,<2.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.mypy]
files = ["{name}_connector/**/*.py"]
python_version = "3.10"
disallow_untyped_defs = true
