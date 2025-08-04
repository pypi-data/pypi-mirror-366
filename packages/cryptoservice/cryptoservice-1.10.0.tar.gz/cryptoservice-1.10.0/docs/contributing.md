# 贡献指南

欢迎为 CryptoService 项目做出贡献！

## 🚀 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请：

1. 在 [GitHub Issues](https://github.com/Mrzai/Xdata/issues) 中搜索是否已有相关问题
2. 如果没有，请创建新的 issue，包含：
   - 清晰的问题描述
   - 重现步骤
   - 预期行为 vs 实际行为
   - 环境信息（Python 版本、操作系统等）

### 提交代码

1. **Fork 项目**
   ```bash
   git clone https://github.com/your-username/Xdata.git
   cd Xdata
   ```

2. **创建开发分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **安装开发依赖**
   ```bash
   pip install -e ".[dev]"
   ```

4. **编写代码和测试**
   - 遵循现有的代码风格
   - 添加适当的测试
   - 更新相关文档

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **推送并创建 Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 开发规范

### 代码风格

- 使用 Python 3.8+ 语法特性
- 遵循 PEP 8 编码规范
- 使用类型提示
- 编写清晰的文档字符串

### 提交信息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
type(scope): description

feat: 新功能
fix: bug 修复
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

### 文档

- 对新功能添加相应的使用示例
- 更新 API 文档
- 在 `CHANGELOG.md` 中记录重要更改

## 🔍 测试

运行测试套件：

```bash
# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest tests/test_specific.py

# 运行测试并查看覆盖率
python -m pytest --cov=cryptoservice
```

## 📚 文档开发

本项目使用 MkDocs 构建文档：

```bash
# 安装文档依赖
pip install -e ".[docs]"

# 本地预览文档
mkdocs serve

# 构建文档
mkdocs build
```

## 💡 开发提示

- 查看 [开发指南](development_guide.md) 了解详细的开发环境设置
- 参考现有代码的实现模式
- 确保新功能与现有 API 设计一致
- 编写清晰的错误消息和日志

## 📞 联系我们

如有任何问题，欢迎通过以下方式联系：

- GitHub Issues: [项目 Issues](https://github.com/Mrzai/Xdata/issues)
- 邮箱: [项目维护者邮箱]

感谢您的贡献！ 🎉
