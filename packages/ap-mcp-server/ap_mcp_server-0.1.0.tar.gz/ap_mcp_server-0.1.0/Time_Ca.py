# -*- coding: utf-8 -*-
"""
通用中文口语化时间解析
支持：
  1) 相对日期：今天/明天/后天/大后天 + 上午/下午/晚上 + 几点(半)
  2) 绝对月日：8月1号上午8点、8月9号下午4点半
返回 datetime 对象
"""

import re
from datetime import datetime, timedelta

# 默认基准时间，可在外部调用时覆盖
BASE = datetime(2025, 7, 30)

# -------------------------------------------------
# 内部工具
# -------------------------------------------------
def _parse_day_month(text: str, base: datetime) -> datetime | None:
    """绝对月日，如 8月1号 -> datetime"""
    m = re.search(r'(\d{1,2})月(\d{1,2})(?:号|日)', text)
    if not m:
        return None
    month, day = int(m.group(1)), int(m.group(2))
    return datetime(base.year, month, day)


def _parse_relative_day(text: str, base: datetime) -> datetime | None:
    """相对日期，如 明天 -> datetime"""
    day_map = {"今天": 0, "明天": 1, "后天": 2, "大后天": 3}
    for k, v in day_map.items():
        if k in text:
            return (base.replace(hour=0, minute=0, second=0, microsecond=0)
                    + timedelta(days=v))
    return None


def _parse_hm(text: str) -> tuple[int, int]:
    """提取小时、分钟，如 3点半 -> (3,30)"""
    hour = minute = 0
    m = re.search(r'(\d{1,2})(?:点(?:(\d{1,2})分|半)?)', text)
    if m:
        hour = int(m.group(1))
        if m.group(2):
            minute = int(m.group(2))
        elif "半" in text:
            minute = 30
    return hour, minute


def _period_offset(text: str) -> int:
    """上午/下午/晚上 对应加多少小时"""
    period_map = {
        "上午": 0, "早晨": 0, "早上": 0,
        "中午": 12,
        "下午": 12,
        "傍晚": 18,
        "晚上": 18
    }
    for k, v in period_map.items():
        if k in text:
            return v
    return 0

# -------------------------------------------------
# 公开函数
# -------------------------------------------------
def parse_single_time(text: str, base: datetime | None = None) -> datetime:
    """解析单点时间描述"""
    base = base or BASE
    day_dt = _parse_day_month(text, base) or _parse_relative_day(text, base)
    if day_dt is None:
        raise ValueError(f"无法识别日期：{text}")

    hour, minute = _parse_hm(text)
    hour += _period_offset(text)
    hour %= 24
    return day_dt.replace(hour=hour, minute=minute)


def parse_range(text: str, base: datetime | None = None) -> tuple[datetime, datetime]:
    """解析区间，如 8月1号上午8点到8月9号下午4点"""
    base = base or BASE
    text = text.replace("从", "")
    parts = re.split(r"[到至]", text)
    if len(parts) != 2:
        raise ValueError("请用“到”或“至”分隔")
    start = parse_single_time(parts[0].strip(), base)
    end = parse_single_time(parts[1].strip(), base)
    return start, end


def fmt_iso(dt: datetime) -> str:
    """返回 ISO 格式 yyyy-mm-dd HH:MM:SS"""
    return dt.strftime('%Y-%m-%d %H:%M:%S')