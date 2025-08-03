# Jupiter Python SDK 测试运行器
# 使用: just <命令>

# 默认命令 - 显示帮助
default:
    @just --list

# 运行单元测试
test-unit:
    @echo "=== 运行单元测试 ==="
    uv run pytest tests -v

# 运行所有测试
test-all:
    @echo "=== 运行所有测试 ==="
    uv run pytest tests -v

# 运行测试并生成覆盖率报告
test-coverage:
    @echo "=== 运行测试并生成覆盖率报告 ==="
    uv run pytest tests --cov=pyjupiter --cov-report=html --cov-report=term
    @echo "覆盖率报告已生成到 htmlcov/index.html"

# 快速测试（只运行快速的单元测试）
test-quick:
    @echo "=== 运行快速测试 ==="
    uv run pytest tests -v -m "not slow"

# 运行特定测试文件
test-file FILE:
    @echo "=== 运行测试文件: {{FILE}} ==="
    uv run pytest {{FILE}} -v

# 运行特定测试函数
test-func FUNC:
    @echo "=== 运行测试函数: {{FUNC}} ==="
    uv run pytest -k {{FUNC}} -v

# 运行 linter
lint:
    @echo "=== 运行代码检查 ==="
    uv run ruff check .
    uv run pyright .

# 格式化代码
format:
    @echo "=== 格式化代码 ==="
    uv run ruff format pyjupiter tests
    uv run ruff check --fix pyjupiter tests

# 检查代码格式
format-check:
    @echo "=== 检查代码格式 ==="
    uv run ruff format --check pyjupiter tests
    uv run ruff check pyjupiter tests

# 清理临时文件
clean:
    @echo "=== 清理临时文件 ==="
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type d -name ".ruff_cache" -exec rm -rf {} +
    find . -type d -name ".pyright" -exec rm -rf {} +
    find . -type d -name ".mypy_cache" -exec rm -rf {} +
    rm -rf htmlcov/
    rm -rf .coverage

# 安装开发依赖
install:
    @echo "=== 安装开发依赖 ==="
    uv sync --all-extras
    @echo "=== 安装 Node.js 依赖 ==="
    pnpm install

# 运行示例
example NAME:
    @echo "=== 运行示例: {{NAME}} ==="
    uv run python examples/{{NAME}}.py

# 完整的 CI 检查（格式化、lint、测试）
ci:
    @echo "=== 运行完整 CI 检查 ==="
    just format-check
    just md-check
    just mermaid-validate
    just yaml-lint
    just lint
    just test-all

# 快速提交（跳过 pre-commit）
commit MSG:
    @echo "=== 快速提交 ==="
    git add -A
    git commit --no-verify -m "{{MSG}}"

# 格式化后提交
commit-format MSG:
    @echo "=== 格式化并提交 ==="
    just format
    git add -A
    git commit --no-verify -m "{{MSG}}"

# 别名 - 更短的命令
# Markdown 格式化命令

# 检查 markdown 格式
md-check:
    @echo "=== 检查 Markdown 格式 ==="
    pnpm run format:md:check

# 格式化 markdown 文件
md-format:
    @echo "=== 格式化 Markdown 文件 ==="
    pnpm run format:md

# 验证 Mermaid 图表
mermaid-validate:
    @echo "=== 验证 Mermaid 图表 ==="
    pnpm run validate:mermaid

# 验证所有 Markdown 文件中的 Mermaid 图表
mermaid-validate-all:
    @echo "=== 验证所有 Markdown 文件中的 Mermaid 图表 ==="
    find docs -name "*.md" -exec npx mermaid-validate validate-md {} \;

# YAML 相关命令

# 检查 YAML 文件
yaml-lint:
    @echo "=== 检查 YAML 文件 ==="
    uv run yamllint .

# 修复 YAML 格式
yaml-fix:
    @echo "=== 修复 YAML 格式 ==="
    uv run yamlfix .

# 文档相关命令

# 文档相关命令
docs-serve:
    @echo "=== 停止文档服务器 ==="
    -lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "文档服务器未运行"
    @echo "=== 启动文档服务器 (后台运行) ==="
    nohup uv run mkdocs serve > mkdocs.log 2>&1 &
    @echo "文档服务器已在后台启动，日志输出到 mkdocs.log"
    @echo "访问: http://localhost:8000"

# 停止文档服务器（杀死端口 8000）
docs-stop:
    @echo "=== 停止文档服务器 ==="
    -lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "文档服务器未运行"


# 构建文档
docs-build:
    just install
    @echo "=== 构建文档 ==="
    mkdocs build

# 部署文档到 GitHub Pages
docs-deploy:
    just install
    @echo "=== 部署文档到 GitHub Pages ==="
    mkdocs gh-deploy

# 检查文档链接
docs-check:
    @echo "=== 检查文档链接 ==="
    @echo "检查 docs/ 目录中的所有 .md 文件..."
    @find docs -name "*.md" -exec echo "📄 {}" \;
    @echo "✅ 文档文件检查完成"

# 创建新的文档文件
docs-new FILE:
    @echo "=== 创建新文档文件: {{FILE}} ==="
    @if [ ! -f "docs/{{FILE}}" ]; then \
        echo "# {{FILE}}" > "docs/{{FILE}}"; \
        echo "✅ 创建了新文档文件: docs/{{FILE}}"; \
    else \
        echo "❌ 文件已存在: docs/{{FILE}}"; \
    fi

# 文档统计
docs-stats:
    @echo "=== 文档统计 ==="
    @echo "📊 文档文件数量:"
    @find docs -name "*.md" | wc -l | xargs echo "  Markdown 文件:"
    @echo "📊 总行数:"
    @find docs -name "*.md" -exec wc -l {} + | tail -1 | awk '{print "  总行数: " $1}'
    @echo "📊 文档大小:"
    @du -sh docs/ | awk '{print "  总大小: " $1}'

# 别名 - 更短的命令
alias t := test-unit
alias ta := test-all
alias tc := test-coverage
alias l := lint
alias f := format
alias c := commit
alias cf := commit-format
alias d := docs-serve
alias ds := docs-stop
alias db := docs-build
alias dd := docs-deploy
alias mc := md-check
alias mf := md-format
alias i := install
