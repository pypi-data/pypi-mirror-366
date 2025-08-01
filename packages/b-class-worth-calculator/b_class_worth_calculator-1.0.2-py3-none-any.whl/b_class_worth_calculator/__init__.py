#!/usr/bin/env python3
"""
🎯 这个B班值不值得上 - 工作性价比计算器
智能分析工作性价比，帮你做出明智的职业选择
"""

__version__ = "1.0.2"
__author__ = "TraeAI"
__email__ = "support@trae.ai"
__description__ = "智能工作性价比分析工具，综合评估薪资、工时、通勤等多维度因素，支持生成可视化报告"

from .main import main, calculate_work_worth, compare_jobs, get_calculation_template, get_ppp_factors, generate_work_report_image

__all__ = ["main", "calculate_work_worth", "compare_jobs", "get_calculation_template", "get_ppp_factors", "generate_work_report_image"]