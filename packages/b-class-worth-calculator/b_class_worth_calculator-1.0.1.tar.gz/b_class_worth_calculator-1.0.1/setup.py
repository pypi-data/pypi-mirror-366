#!/usr/bin/env python3
"""
这个B班值不值得上 - 工作性价比计算器
PyPI发布配置文件
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="b-class-worth-calculator",
    version="1.0.1",
    author="TraeAI",
    author_email="support@trae.ai",
    description="智能工作性价比分析工具，综合评估薪资、工时、通勤等多维度因素，支持生成可视化报告",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trae-ai/b-class-worth-calculator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "fastmcp>=0.1.0",
        "playwright>=1.40.0",
        "jinja2>=3.1.0",
        "pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "b-class-worth-calculator=b_class_worth_calculator.main:main",
        ],
    },
    keywords=[
        "job", "salary", "calculator", "work", "worth", "analysis", 
        "career", "mcp", "tool", "productivity", "visualization",
        "工作", "薪资", "计算器", "性价比", "分析", "职业"
    ],
    project_urls={
        "Bug Reports": "https://github.com/trae-ai/b-class-worth-calculator/issues",
        "Source": "https://github.com/trae-ai/b-class-worth-calculator",
        "Documentation": "https://github.com/trae-ai/b-class-worth-calculator/blob/main/README.md",
    },
)