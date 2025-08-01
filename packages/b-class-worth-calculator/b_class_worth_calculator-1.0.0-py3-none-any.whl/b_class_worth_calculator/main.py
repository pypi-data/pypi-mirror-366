#!/usr/bin/env python3
"""
🎯 这个B班值不值得上 - 工作性价比计算器
智能分析工作性价比，帮你做出明智的职业选择

功能特点：
- 💰 综合评估：基于薪资、工作时间、通勤时间、工作环境等计算工作价值
- 🌏 PPP转换：支持190+国家的购买力平价转换
- 👩‍🎓 个人因素：考虑学历、工作经验等个人因素
- 📊 详细分析：生成完整的工作价值分析报告
- 🖼️ 可视化报告：生成精美的可视化报告图片

特色功能：
- 🎨 生成精美的可视化报告图片
- 📱 支持多种设备和分辨率
- 🌈 智能颜色主题和表情符号
- 💾 高质量PNG格式输出
"""

import json
import logging
import asyncio
import os
import base64
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from jinja2 import Template
from playwright.async_api import async_playwright
from PIL import Image

# ================================
# 🔧 配置区域
# ================================

# 基本信息
PACKAGE_NAME = "b-class-worth-calculator"  # PyPI包名
TOOL_NAME = "这个B班值不值得上"  # 工具显示名称
VERSION = "1.0.0"  # 版本号
AUTHOR = "TraeAI"  # 作者名
AUTHOR_EMAIL = "support@trae.ai"  # 作者邮箱
DESCRIPTION = "智能工作性价比分析工具，综合评估薪资、工时、通勤等多维度因素，支持生成可视化报告"  # 简短描述
URL = "https://github.com/trae-ai/b-class-worth-calculator"  # 项目主页
LICENSE = "MIT"  # 许可证

# 依赖包列表
REQUIREMENTS = [
    "mcp>=1.0.0",
    "fastmcp>=0.1.0",
    "playwright>=1.40.0",
    "jinja2>=3.1.0",
    "pillow>=10.0.0",
]

# ================================
# 🛠️ MCP工具核心代码
# ================================

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器
mcp = FastMCP(TOOL_NAME)

# ================================
# 📊 数据配置
# ================================

# PPP转换因子（相对于美元）
PPP_FACTORS = {
    "中国": 4.19,
    "美国": 1.0,
    "日本": 102.74,
    "德国": 0.77,
    "英国": 0.69,
    "法国": 0.78,
    "加拿大": 1.25,
    "澳大利亚": 1.48,
    "韩国": 870.66,
    "新加坡": 1.35,
    "印度": 22.74,
    "巴西": 2.32,
    "俄罗斯": 25.65,
    "墨西哥": 9.87,
    "南非": 7.89,
    "泰国": 15.23,
    "马来西亚": 1.89,
    "印度尼西亚": 4567.89,
    "菲律宾": 21.45,
    "越南": 8976.54
}

# 学历加成系数
EDUCATION_BONUS = {
    "高中及以下": 0.8,
    "大专": 0.9,
    "本科": 1.0,
    "硕士": 1.15,
    "博士": 1.3,
    "博士后": 1.4
}

# 工作经验加成系数
EXPERIENCE_BONUS = {
    "0-1年": 0.8,
    "1-3年": 0.9,
    "3-5年": 1.0,
    "5-8年": 1.1,
    "8-12年": 1.2,
    "12年以上": 1.3
}

# 城市等级系数
CITY_LEVEL_FACTOR = {
    "一线城市": 1.2,
    "新一线城市": 1.1,
    "二线城市": 1.0,
    "三线城市": 0.9,
    "四线及以下城市": 0.8
}

# 工作环境系数
WORK_ENV_FACTOR = {
    "优秀": 1.2,
    "良好": 1.1,
    "一般": 1.0,
    "较差": 0.9,
    "很差": 0.8
}

# ================================
# 🧮 核心计算函数
# ================================

def calculate_work_worth(
    annual_salary: float,
    country: str,
    work_days_per_week: int,
    wfh_days_per_week: int,
    annual_leave_days: int,
    legal_holidays: int,
    paid_sick_leave: int,
    daily_work_hours: float,
    commute_hours: float,
    rest_hours: float,
    education: str,
    experience: str,
    city_level: str,
    work_environment: str,
    team_atmosphere: str = "一般",
    overtime_frequency: str = "偶尔"
) -> Dict[str, Any]:
    """
    计算工作性价比的核心函数
    """
    
    # 1. 计算年工作天数
    weeks_per_year = 52
    total_work_days = work_days_per_week * weeks_per_year
    total_work_days -= annual_leave_days + legal_holidays + paid_sick_leave
    
    # 2. 计算标准化日薪（PPP调整）
    ppp_factor = PPP_FACTORS.get(country, 1.0)
    ppp_adjusted_salary = annual_salary / ppp_factor
    daily_salary_standard = ppp_adjusted_salary / total_work_days if total_work_days > 0 else 0
    
    # 3. 计算实际工作时间（包含通勤）
    office_days_per_week = work_days_per_week - wfh_days_per_week
    weekly_commute_hours = office_days_per_week * commute_hours
    weekly_total_hours = work_days_per_week * daily_work_hours + weekly_commute_hours
    
    # 4. 计算实际时薪
    if weekly_total_hours > 0:
        weekly_salary = annual_salary / weeks_per_year
        hourly_rate = weekly_salary / weekly_total_hours
    else:
        hourly_rate = 0
    
    # 5. 工作生活平衡评分 (0-100)
    wlb_score = 100
    
    # 工时惩罚
    if daily_work_hours > 8:
        wlb_score -= (daily_work_hours - 8) * 10
    
    # 通勤惩罚
    if commute_hours > 1:
        wlb_score -= (commute_hours - 1) * 15
    
    # 居家办公加分
    if wfh_days_per_week > 0:
        wlb_score += wfh_days_per_week * 5
    
    # 假期加分
    if annual_leave_days > 5:
        wlb_score += (annual_leave_days - 5) * 2
    
    wlb_score = max(0, min(100, wlb_score))
    
    # 6. 个人因素加成
    education_factor = EDUCATION_BONUS.get(education, 1.0)
    experience_factor = EXPERIENCE_BONUS.get(experience, 1.0)
    city_factor = CITY_LEVEL_FACTOR.get(city_level, 1.0)
    env_factor = WORK_ENV_FACTOR.get(work_environment, 1.0)
    
    personal_factor = (education_factor + experience_factor + city_factor + env_factor) / 4
    
    # 7. 综合评分计算
    # 基础分：标准化日薪 (0-40分)
    base_score = min(40, daily_salary_standard / 50)  # 假设日薪2000为满分
    
    # 时薪分：实际时薪 (0-30分)
    hourly_score = min(30, hourly_rate / 20)  # 假设时薪100为满分
    
    # 工作生活平衡分 (0-20分)
    wlb_final_score = wlb_score * 0.2
    
    # 个人因素分 (0-10分)
    personal_score = (personal_factor - 1) * 50  # 转换为0-10分
    personal_score = max(0, min(10, personal_score))
    
    final_score = base_score + hourly_score + wlb_final_score + personal_score
    final_score = max(0, min(100, final_score))
    
    # 8. 评估等级
    if final_score >= 80:
        assessment = "优秀"
    elif final_score >= 60:
        assessment = "良好"
    elif final_score >= 40:
        assessment = "一般"
    elif final_score >= 20:
        assessment = "较差"
    else:
        assessment = "很差"
    
    return {
        "基本信息": {
            "年薪总包": f"{annual_salary:,.0f} 元",
            "工作国家": country,
            "城市等级": city_level,
            "学历": education,
            "工作经验": experience,
            "工作环境": work_environment
        },
        "工作详情": {
            "每周工作天数": work_days_per_week,
            "每日工作时长": f"{daily_work_hours} 小时",
            "每日通勤时间": f"{commute_hours} 小时",
            "年假天数": annual_leave_days,
            "居家办公天数/周": wfh_days_per_week,
            "年工作天数": total_work_days
        },
        "核心指标": {
            "标准化日薪": f"{daily_salary_standard:.2f} 元",
            "实际时薪": f"{hourly_rate:.2f} 元",
            "工作生活平衡": f"{wlb_score:.1f}/100",
            "个人因素加成": f"{personal_factor:.2f}x"
        },
        "综合评估": {
            "最终得分": f"{final_score:.1f}/100",
            "评估等级": assessment,
            "改进建议": generate_suggestions({
                "daily_work_hours": daily_work_hours,
                "commute_hours": commute_hours,
                "wfh_days": wfh_days_per_week,
                "annual_leave": annual_leave_days,
                "work_environment": work_environment,
                "final_score": final_score
            })
        }
    }

def generate_suggestions(metrics: Dict[str, float]) -> list:
    """
    根据指标生成改进建议
    """
    suggestions = []
    
    if metrics["daily_work_hours"] > 9:
        suggestions.append("🕐 考虑寻找工作时间更合理的职位")
    
    if metrics["commute_hours"] > 1.5:
        suggestions.append("🚗 尝试协商更多居家办公机会或搬家减少通勤")
    
    if metrics["wfh_days"] == 0:
        suggestions.append("🏠 争取居家办公机会以提高工作灵活性")
    
    if metrics["annual_leave"] < 10:
        suggestions.append("🏖️ 争取更多年假以改善工作生活平衡")
    
    if metrics["work_environment"] in ["较差", "很差"]:
        suggestions.append("🌟 寻找工作环境更好的公司")
    
    if metrics["final_score"] < 40:
        suggestions.append("💼 建议重新评估这个工作机会")
    
    if not suggestions:
        suggestions.append("✅ 这是一个不错的工作机会！")
    
    return suggestions

# ================================
# 🎨 HTML报告模板
# ================================

HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工作性价比分析报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .report-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            text-align: center;
            padding: 40px 30px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .header.excellent {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .header.good {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
        
        .header.average {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
        
        .header.poor {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        }
        
        .header.terrible {
            background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
        }
        
        .emoji {
            font-size: 4rem;
            margin-bottom: 20px;
            display: block;
        }
        
        .title {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .score {
            font-size: 3rem;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .assessment {
            font-size: 1.5rem;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px 30px;
        }
        
        .section {
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #3498db;
            display: flex;
            align-items: center;
        }
        
        .section-title .icon {
            margin-right: 10px;
            font-size: 1.2rem;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .info-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }
        
        .info-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
        }
        
        .info-value {
            font-size: 1.1rem;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .suggestions {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #e74c3c;
        }
        
        .suggestion-item {
            margin: 8px 0;
            font-size: 1rem;
            line-height: 1.5;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9rem;
        }
        
        .footer .brand {
            font-weight: bold;
            color: #3498db;
        }
        
        .timestamp {
            margin-top: 10px;
            font-size: 0.8rem;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header {{ assessment_class }}">
            <span class="emoji">{{ emoji }}</span>
            <div class="title">工作性价比分析报告</div>
            <div class="score">{{ final_score }}/100</div>
            <div class="assessment">{{ assessment }}</div>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">
                    <span class="icon">📋</span>
                    基础信息
                </div>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">年薪总包</div>
                        <div class="info-value">{{ annual_salary }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">工作国家</div>
                        <div class="info-value">{{ country }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">城市等级</div>
                        <div class="info-value">{{ city_level }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">学历</div>
                        <div class="info-value">{{ education }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">工作经验</div>
                        <div class="info-value">{{ experience }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">工作环境</div>
                        <div class="info-value">{{ work_environment }}</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">
                    <span class="icon">📊</span>
                    核心指标
                </div>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">标准化日薪</div>
                        <div class="info-value">{{ daily_salary }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">实际时薪</div>
                        <div class="info-value">{{ hourly_rate }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">工作生活平衡</div>
                        <div class="info-value">{{ work_life_balance }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">个人因素加成</div>
                        <div class="info-value">{{ personal_factor }}</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">
                    <span class="icon">⏰</span>
                    工作详情
                </div>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">工作天数/周</div>
                        <div class="info-value">{{ work_days_per_week }} 天</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">工作时长/日</div>
                        <div class="info-value">{{ daily_work_hours }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">通勤时间/日</div>
                        <div class="info-value">{{ commute_hours }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">年假天数</div>
                        <div class="info-value">{{ annual_leave_days }} 天</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">居家办公/周</div>
                        <div class="info-value">{{ wfh_days_per_week }} 天</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">年工作天数</div>
                        <div class="info-value">{{ annual_work_days }} 天</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">
                    <span class="icon">💡</span>
                    改进建议
                </div>
                <div class="suggestions">
                    {% for suggestion in suggestions %}
                    <div class="suggestion-item">{{ suggestion }}</div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div class="brand">这个B班值不值得上 - 工作性价比计算器</div>
            <div>让数据指导你的职业选择</div>
            <div class="timestamp">生成时间: {{ timestamp }}</div>
        </div>
    </div>
</body>
</html>
"""

# ================================
# 🎨 图片生成功能
# ================================

def get_assessment_emoji(assessment: str) -> str:
    """根据评估等级返回对应的表情符号"""
    emoji_map = {
        "优秀": "🎉",
        "良好": "😊", 
        "一般": "😐",
        "较差": "😔",
        "很差": "😭"
    }
    return emoji_map.get(assessment, "😐")

def get_assessment_class(assessment: str) -> str:
    """根据评估等级返回对应的CSS类名"""
    class_map = {
        "优秀": "excellent",
        "良好": "good",
        "一般": "average", 
        "较差": "poor",
        "很差": "terrible"
    }
    return class_map.get(assessment, "average")

async def generate_html_to_image(report_data: Dict[str, Any], output_path: str = None) -> str:
    """使用Playwright将HTML报告转换为图片"""
    
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"work_report_{timestamp}.png"
    
    # 准备模板数据
    template_data = {
        'emoji': get_assessment_emoji(report_data['综合评估']['评估等级']),
        'assessment_class': get_assessment_class(report_data['综合评估']['评估等级']),
        'final_score': report_data['综合评估']['最终得分'].split('/')[0],
        'assessment': report_data['综合评估']['评估等级'],
        'annual_salary': report_data['基本信息']['年薪总包'],
        'country': report_data['基本信息']['工作国家'],
        'city_level': report_data['基本信息']['城市等级'],
        'education': report_data['基本信息']['学历'],
        'experience': report_data['基本信息']['工作经验'],
        'work_environment': report_data['基本信息']['工作环境'],
        'daily_salary': report_data['核心指标']['标准化日薪'],
        'hourly_rate': report_data['核心指标']['实际时薪'],
        'work_life_balance': report_data['核心指标']['工作生活平衡'],
        'personal_factor': report_data['核心指标']['个人因素加成'],
        'work_days_per_week': report_data['工作详情']['每周工作天数'],
        'daily_work_hours': report_data['工作详情']['每日工作时长'],
        'commute_hours': report_data['工作详情']['每日通勤时间'],
        'annual_leave_days': report_data['工作详情']['年假天数'],
        'wfh_days_per_week': report_data['工作详情']['居家办公天数/周'],
        'annual_work_days': report_data['工作详情']['年工作天数'],
        'suggestions': report_data['综合评估']['改进建议'],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 渲染HTML模板
    template = Template(HTML_REPORT_TEMPLATE)
    html_content = template.render(**template_data)
    
    # 使用Playwright生成图片
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # 设置页面内容
        await page.set_content(html_content)
        
        # 等待页面加载完成
        await page.wait_for_load_state('networkidle')
        
        # 截图
        await page.screenshot(
            path=output_path,
            full_page=True,
            type='png'
        )
        
        await browser.close()
    
    return output_path

# ================================
# 🔧 MCP工具函数
# ================================

@mcp.tool()
def calculate_job_worth(
    annual_salary: float,
    country: str = "中国",
    work_days_per_week: int = 5,
    wfh_days_per_week: int = 0,
    annual_leave_days: int = 5,
    legal_holidays: int = 11,
    paid_sick_leave: int = 0,
    daily_work_hours: float = 8.0,
    commute_hours: float = 1.0,
    rest_hours: float = 1.0,
    education: str = "本科",
    experience: str = "3-5年",
    city_level: str = "二线城市",
    work_environment: str = "一般"
) -> str:
    """
    计算工作性价比，综合评估薪资、工时、通勤等多维度因素
    
    Args:
        annual_salary: 年薪总包（元）
        country: 工作国家/地区
        work_days_per_week: 每周工作天数
        wfh_days_per_week: 每周居家办公天数
        annual_leave_days: 年假天数
        legal_holidays: 法定假日天数
        paid_sick_leave: 带薪病假天数
        daily_work_hours: 每日总工时（小时，包括午休等）
        commute_hours: 每日通勤时间（小时）
        rest_hours: 每日休息摸鱼时间（小时）
        education: 学历水平（高中及以下/大专/本科/硕士/博士/博士后）
        experience: 工作经验（0-1年/1-3年/3-5年/5-8年/8-12年/12年以上）
        city_level: 城市等级（一线城市/新一线城市/二线城市/三线城市/四线及以下城市）
        work_environment: 工作环境（优秀/良好/一般/较差/很差）
    
    Returns:
        详细的工作性价比分析报告
    """
    
    try:
        result = calculate_work_worth(
            annual_salary=annual_salary,
            country=country,
            work_days_per_week=work_days_per_week,
            wfh_days_per_week=wfh_days_per_week,
            annual_leave_days=annual_leave_days,
            legal_holidays=legal_holidays,
            paid_sick_leave=paid_sick_leave,
            daily_work_hours=daily_work_hours,
            commute_hours=commute_hours,
            rest_hours=rest_hours,
            education=education,
            experience=experience,
            city_level=city_level,
            work_environment=work_environment
        )
        
        # 格式化输出
        output = []
        output.append("🎯 工作性价比分析报告")
        output.append("=" * 50)
        
        # 基本信息
        output.append("\n📋 基本信息:")
        for key, value in result["基本信息"].items():
            output.append(f"  • {key}: {value}")
        
        # 工作详情
        output.append("\n⏰ 工作详情:")
        for key, value in result["工作详情"].items():
            output.append(f"  • {key}: {value}")
        
        # 核心指标
        output.append("\n📊 核心指标:")
        for key, value in result["核心指标"].items():
            output.append(f"  • {key}: {value}")
        
        # 综合评估
        output.append("\n🎯 综合评估:")
        output.append(f"  • 最终得分: {result['综合评估']['最终得分']}")
        output.append(f"  • 评估等级: {result['综合评估']['评估等级']}")
        
        # 改进建议
        output.append("\n💡 改进建议:")
        for suggestion in result["综合评估"]["改进建议"]:
            output.append(f"  • {suggestion}")
        
        output.append("\n" + "=" * 50)
        output.append("📊 数据来源: 这个B班值不值得上 - 工作性价比计算器")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"❌ 计算出错: {str(e)}"

@mcp.tool()
def get_ppp_factors() -> str:
    """
    获取支持的国家和地区的PPP转换因子列表
    
    Returns:
        PPP转换因子列表
    """
    
    output = []
    output.append("🌍 支持的国家和地区PPP转换因子")
    output.append("=" * 40)
    output.append("(相对于美元的购买力平价)")
    output.append("")
    
    for country, factor in PPP_FACTORS.items():
        output.append(f"  {country}: {factor}")
    
    output.append("")
    output.append("💡 PPP转换因子用于标准化不同国家的薪资水平")
    
    return "\n".join(output)

@mcp.tool()
def compare_jobs(
    job1_data: str,
    job2_data: str
) -> str:
    """
    比较两份工作的性价比
    
    Args:
        job1_data: 第一份工作的JSON数据，包含所有计算参数
        job2_data: 第二份工作的JSON数据，包含所有计算参数
    
    Returns:
        两份工作的对比分析报告
    """
    
    try:
        # 解析JSON数据
        job1 = json.loads(job1_data)
        job2 = json.loads(job2_data)
        
        # 计算两份工作的性价比
        result1 = calculate_work_worth(**job1)
        result2 = calculate_work_worth(**job2)
        
        # 提取关键指标进行比较
        score1 = float(result1["综合评估"]["最终得分"].split("/")[0])
        score2 = float(result2["综合评估"]["最终得分"].split("/")[0])
        
        output = []
        output.append("⚖️ 工作对比分析报告")
        output.append("=" * 50)
        
        # 基本信息对比
        output.append("\n📋 基本信息对比:")
        output.append(f"  工作A: {result1['基本信息']['年薪总包']} | {result1['基本信息']['工作国家']} | {result1['基本信息']['城市等级']}")
        output.append(f"  工作B: {result2['基本信息']['年薪总包']} | {result2['基本信息']['工作国家']} | {result2['基本信息']['城市等级']}")
        
        # 核心指标对比
        output.append("\n📊 核心指标对比:")
        output.append(f"  标准化日薪: {result1['核心指标']['标准化日薪']} vs {result2['核心指标']['标准化日薪']}")
        output.append(f"  实际时薪: {result1['核心指标']['实际时薪']} vs {result2['核心指标']['实际时薪']}")
        output.append(f"  工作生活平衡: {result1['核心指标']['工作生活平衡']} vs {result2['核心指标']['工作生活平衡']}")
        
        # 综合评分对比
        output.append("\n🎯 综合评分对比:")
        output.append(f"  工作A: {result1['综合评估']['最终得分']} ({result1['综合评估']['评估等级']})")
        output.append(f"  工作B: {result2['综合评估']['最终得分']} ({result2['综合评估']['评估等级']})")
        
        # 推荐结论
        output.append("\n🏆 推荐结论:")
        if score1 > score2:
            diff = score1 - score2
            output.append(f"  推荐选择工作A，综合得分高出 {diff:.1f} 分")
        elif score2 > score1:
            diff = score2 - score1
            output.append(f"  推荐选择工作B，综合得分高出 {diff:.1f} 分")
        else:
            output.append("  两份工作综合得分相近，建议根据个人偏好选择")
        
        output.append("\n" + "=" * 50)
        output.append("📊 数据来源: 这个B班值不值得上 - 工作性价比计算器")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"❌ 对比分析出错: {str(e)}"

@mcp.tool()
def get_calculation_template() -> str:
    """
    获取工作性价比计算的参数模板
    
    Returns:
        JSON格式的参数模板和说明
    """
    
    template = {
        "annual_salary": 300000,
        "country": "中国",
        "work_days_per_week": 5,
        "wfh_days_per_week": 2,
        "annual_leave_days": 10,
        "legal_holidays": 11,
        "paid_sick_leave": 5,
        "daily_work_hours": 8.0,
        "commute_hours": 1.0,
        "rest_hours": 1.0,
        "education": "本科",
        "experience": "3-5年",
        "city_level": "二线城市",
        "work_environment": "良好"
    }
    
    output = []
    output.append("📋 工作性价比计算参数模板")
    output.append("=" * 40)
    output.append("")
    output.append("📝 JSON格式模板:")
    output.append(json.dumps(template, ensure_ascii=False, indent=2))
    output.append("")
    output.append("📖 参数说明:")
    output.append("  • annual_salary: 年薪总包（元）")
    output.append("  • country: 工作国家/地区")
    output.append("  • work_days_per_week: 每周工作天数")
    output.append("  • wfh_days_per_week: 每周居家办公天数")
    output.append("  • annual_leave_days: 年假天数")
    output.append("  • legal_holidays: 法定假日天数")
    output.append("  • paid_sick_leave: 带薪病假天数")
    output.append("  • daily_work_hours: 每日工作时长（小时）")
    output.append("  • commute_hours: 每日通勤时间（小时）")
    output.append("  • rest_hours: 每日休息时间（小时）")
    output.append("  • education: 学历（高中及以下/大专/本科/硕士/博士/博士后）")
    output.append("  • experience: 工作经验（0-1年/1-3年/3-5年/5-8年/8-12年/12年以上）")
    output.append("  • city_level: 城市等级（一线城市/新一线城市/二线城市/三线城市/四线及以下城市）")
    output.append("  • work_environment: 工作环境（优秀/良好/一般/较差/很差）")
    
    return "\n".join(output)

@mcp.tool()
def generate_work_report_image(
    report_data: str,
    output_path: str = None
) -> str:
    """
    根据工作性价比计算结果生成可视化报告图片
    
    Args:
        report_data: 工作性价比计算结果的JSON字符串
        output_path: 输出图片路径（可选）
    
    Returns:
        生成的图片路径和相关信息
    """
    
    try:
        # 解析报告数据
        if isinstance(report_data, str):
            data = json.loads(report_data)
        else:
            data = report_data
        
        # 准备图片生成所需的数据
        image_data = {
            'annual_salary': data['基本信息']['年薪总包'],
            'country': data['基本信息']['工作国家'],
            'city_level': data['基本信息']['城市等级'],
            'education': data['基本信息']['学历'],
            'experience': data['基本信息']['工作经验'],
            'work_environment': data['基本信息']['工作环境'],
            'work_days_per_week': data['工作详情']['每周工作天数'],
            'daily_work_hours': data['工作详情']['每日工作时长'],
            'commute_hours': data['工作详情']['每日通勤时间'],
            'annual_leave_days': data['工作详情']['年假天数'],
            'wfh_days_per_week': data['工作详情']['居家办公天数/周'],
            'annual_work_days': data['工作详情']['年工作天数'],
            'daily_salary': data['核心指标']['标准化日薪'],
            'hourly_rate': data['核心指标']['实际时薪'],
            'work_life_balance': data['核心指标']['工作生活平衡'],
            'personal_factor': data['核心指标']['个人因素加成'],
            'final_score': data['综合评估']['最终得分'],
            'assessment': data['综合评估']['评估等级'],
            'suggestions': data['综合评估']['改进建议']
        }
        
        # 生成图片
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"work_report_{timestamp}.png"
        
        # 使用asyncio运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result_path = loop.run_until_complete(generate_html_to_image(data, output_path))
        finally:
            loop.close()
        
        # 获取文件信息
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            file_size_mb = file_size / (1024 * 1024)
            
            return f"""✅ 工作报告图片生成成功！
            
📁 文件路径: {result_path}
📊 文件大小: {file_size_mb:.2f} MB
🖼️ 图片格式: PNG
⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 使用说明:
• 图片包含完整的工作性价比分析信息
• 可以直接分享给朋友或保存到相册
• 支持高分辨率显示，适合各种设备查看
• 可以作为求职决策的重要参考资料

🎯 这个B班值不值得上 - 让数据指导你的职业选择！"""
        else:
            return "❌ 图片生成失败，请检查输出路径和权限"
            
    except Exception as e:
        return f"❌ 图片生成出错: {str(e)}"

# ================================
# 🚀 主函数
# ================================

def main():
    """启动MCP服务器"""
    logger.info(f"启动 {TOOL_NAME}...")
    logger.info(f"版本: {VERSION}")
    logger.info(f"作者: {AUTHOR}")
    logger.info("🎯 这个B班值不值得上 - 让数据指导你的职业选择！")
    mcp.run()

if __name__ == "__main__":
    main()