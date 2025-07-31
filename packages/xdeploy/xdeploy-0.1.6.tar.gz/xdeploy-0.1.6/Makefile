# Makefile for Python project management

# 配置变量
PYTHON_VERSIONS := 3.8 3.9 3.10 3.11 3.12
PACKAGE_NAME := xdeploy
TEST_PATH := tests/
SOURCE_PATH := $(PACKAGE_NAME)/

# 默认目标
.DEFAULT_GOAL := help

# 声明伪目标
.PHONY: help install install-pythons dev-install format lint test test-all-versions \
        test-version clean build publish check-deps security-check coverage \
        docs docs-serve pre-commit all

# 颜色定义
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# 帮助信息
help:
	@echo "$(BLUE)Python 项目管理命令:$(NC)"
	@echo ""
	@echo "$(YELLOW)安装相关:$(NC)"
	@echo "  make install           : 安装项目依赖"
	@echo "  make install-pythons   : 安装所有支持的 Python 版本"
	@echo "  make dev-install       : 安装开发依赖"
	@echo ""
	@echo "$(YELLOW)代码质量:$(NC)"
	@echo "  make format            : 格式化代码"
	@echo "  make lint              : 运行 linter"
	@echo "  make check-deps        : 检查依赖安全性"
	@echo "  make security-check    : 安全检查"
	@echo ""
	@echo "$(YELLOW)测试相关:$(NC)"
	@echo "  make test              : 运行测试"
	@echo "  make test-all-versions : 在所有 Python 版本上测试"
	@echo "  make test-version VER=3.9 : 在指定版本上测试"
	@echo "  make coverage          : 生成测试覆盖率报告"
	@echo ""
	@echo "$(YELLOW)构建发布:$(NC)"
	@echo "  make build             : 构建包"
	@echo "  make publish           : 发布到 PyPI"
	@echo "  make clean             : 清理构建产物"
	@echo ""
	@echo "$(YELLOW)文档相关:$(NC)"
	@echo "  make docs              : 构建文档"
	@echo "  make docs-serve        : 启动文档服务器"
	@echo ""
	@echo "$(YELLOW)其他:$(NC)"
	@echo "  make pre-commit        : 运行预提交检查"
	@echo "  make all               : 完整的开发流程"

# 检查 uv 是否安装
check-uv:
	@command -v uv >/dev/null 2>&1 || { echo "$(RED)错误: uv 未安装$(NC)"; exit 1; }

# 安装依赖
install: check-uv
	@echo "$(GREEN)正在安装项目依赖...$(NC)"
	uv sync
	@echo "$(GREEN)依赖安装完成$(NC)"

# 安装所有支持的 Python 版本
install-pythons: check-uv
	@echo "$(GREEN)正在安装 Python 版本: $(PYTHON_VERSIONS)$(NC)"
	@for version in $(PYTHON_VERSIONS); do \
		echo "安装 Python $$version..."; \
		uv python install $$version || echo "$(YELLOW)警告: Python $$version 安装失败$(NC)"; \
	done
	@echo "$(GREEN)Python 版本安装完成$(NC)"

# 开发环境安装
dev-install: install
	@echo "$(GREEN)正在安装开发依赖...$(NC)"
	uv sync --dev
	@echo "$(GREEN)开发环境安装完成$(NC)"

# 格式化代码
format: check-uv
	@echo "$(GREEN)正在格式化代码...$(NC)"
	uv run ruff format .
	@echo "$(GREEN)代码格式化完成$(NC)"

# 运行 linter
lint: check-uv
	@echo "$(GREEN)正在运行 linter...$(NC)"
	uv run ruff check . --fix
	@echo "$(GREEN)Linter 检查完成$(NC)"

# 检查依赖
check-deps: check-uv
	@echo "$(GREEN)正在检查依赖...$(NC)"
	uv run pip-audit || echo "$(YELLOW)警告: pip-audit 未安装，跳过依赖检查$(NC)"

# 安全检查
security-check: check-uv
	@echo "$(GREEN)正在进行安全检查...$(NC)"
	uv run bandit -r $(SOURCE_PATH) || echo "$(YELLOW)警告: bandit 未安装，跳过安全检查$(NC)"

# 运行测试
test: check-uv
	@echo "$(GREEN)正在运行测试...$(NC)"
	uv run pytest $(TEST_PATH) -v
	@echo "$(GREEN)测试完成$(NC)"

# 在指定版本上测试
test-version: check-uv
	@if [ -z "$(VER)" ]; then \
		echo "$(RED)错误: 请指定版本，例如: make test-version VER=3.9$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)正在 Python $(VER) 上运行测试...$(NC)"
	uv run --python $(VER) pytest $(TEST_PATH) -v
	@echo "$(GREEN)Python $(VER) 测试完成$(NC)"

# 在所有版本上测试
test-all-versions: check-uv
	@echo "$(GREEN)正在所有 Python 版本上运行测试...$(NC)"
	@failed_versions=""; \
	for version in $(PYTHON_VERSIONS); do \
		echo "$(BLUE)测试 Python $$version...$(NC)"; \
		if ! uv run --python $$version pytest $(TEST_PATH) -v; then \
			failed_versions="$$failed_versions $$version"; \
			echo "$(RED)Python $$version 测试失败$(NC)"; \
		else \
			echo "$(GREEN)Python $$version 测试通过$(NC)"; \
		fi; \
	done; \
	if [ -n "$$failed_versions" ]; then \
		echo "$(RED)失败的版本:$$failed_versions$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)所有版本测试通过$(NC)"; \
	fi

# 生成覆盖率报告
coverage: check-uv
	@echo "$(GREEN)正在生成测试覆盖率报告...$(NC)"
	uv run pytest $(TEST_PATH) --cov=$(SOURCE_PATH) --cov-report=html --cov-report=term
	@echo "$(GREEN)覆盖率报告生成完成，查看 htmlcov/index.html$(NC)"

# 清理构建产物
clean:
	@echo "$(GREEN)正在清理构建产物...$(NC)"
	rm -rf build dist .eggs *.egg-info .pytest_cache .ruff_cache htmlcov .coverage
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)清理完成$(NC)"

# 构建包
build: clean check-uv
	@echo "$(GREEN)正在构建包...$(NC)"
	uv build
	@echo "$(GREEN)构建完成$(NC)"

# 发布到 PyPI
publish: clean build check-uv
	@echo "$(GREEN)正在发布到 PyPI...$(NC)"
	@uv publish --index hx-pypi; \
	echo "$(GREEN)发布完成$(NC)"; \

# 构建文档
docs: check-uv
	@echo "$(GREEN)正在构建文档...$(NC)"
	uv run mkdocs build
	@echo "$(GREEN)文档构建完成$(NC)"

# 启动文档服务器
docs-serve: check-uv
	@echo "$(GREEN)正在启动文档服务器...$(NC)"
	uv run mkdocs serve

# 预提交检查
pre-commit: format lint test
	@echo "$(GREEN)预提交检查完成$(NC)"

# 完整的开发流程
all: dev-install format lint test coverage
	@echo "$(GREEN)完整开发流程执行完成$(NC)"

# 显示项目信息
info:
	@echo "$(BLUE)项目信息:$(NC)"
	@echo "  包名: $(PACKAGE_NAME)"
	@echo "  测试路径: $(TEST_PATH)"
	@echo "  源码路径: $(SOURCE_PATH)"
	@echo "  支持的 Python 版本: $(PYTHON_VERSIONS)"
	@echo ""
	@echo "$(BLUE)当前环境:$(NC)"
	@uv run python --version 2>/dev/null || echo "  Python: 未安装"
	@uv --version 2>/dev/null || echo "  uv: 未安装"
