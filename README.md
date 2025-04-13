# LLM 学习项目

## 项目简介
本项目用于学习和实践大型语言模型(LLM)的调用和使用。

## 安装步骤
1. 克隆本仓库
2. 安装依赖：
```bash
# 使用uv同步依赖
uv sync

# 其他常用uv命令
uv add package_name  # 安装单个包
uv run script.py      # 运行Python脚本
```
3. 设置环境变量：
```bash
cp .env_example .env
```
然后在.env文件中设置DASHSCOPE_API_KEY

## 使用方法
1. 直接运行测试：
```bash
# 使用python运行测试
python -m pytest

# 或者使用uv运行测试
uv run python -m pytest
```
2. 调用LLM：
```python
from llm import llm_call

response = llm_call("你的问题")
print(response)
```

## 项目结构
- llm.py: LLM调用核心逻辑
- llm_test.py: LLM测试用例
- basic_workflow.py: 工作流核心逻辑，包含链式、并行、路由等处理模式
- workflow_test.py: 工作流测试用例