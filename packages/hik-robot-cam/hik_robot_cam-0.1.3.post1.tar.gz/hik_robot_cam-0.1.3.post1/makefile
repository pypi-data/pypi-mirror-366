# Makefile for HikRobotCamera.PY package
.PHONY: all build publish clean help

# 默认目标
all: build publish

# 构建包
build: clean
	@echo "构建包..."
	uv build
	@echo "构建完成"

# 发布包到仓库
publish:
	@echo "发布包到仓库..."
	uv publish
	@echo "发布完成"

# 清理构建文件
clean:
	@echo "清理构建文件..."
	rm -rf dist/
	@echo "清理完成"

# 显示帮助信息
help:
	@echo "可用命令:"
	@echo "  make build     - 构建包"
	@echo "  make publish   - 发布包到仓库"
	@echo "  make clean     - 清理构建文件"
	@echo "  make all       - 执行构建和发布"
	@echo "  make help      - 显示此帮助信息"
