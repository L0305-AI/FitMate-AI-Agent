from langchain_core.tools import tool
import datetime

@tool
def set_health_reminder(reminder_type: str, time_str: str) -> str:
    """
    设置健康提醒（如喝水、训练）。
    参数:
    reminder_type: 提醒类型，例如 "喝水" 或 "训练"。
    time_str: 提醒时间，格式为 "HH:MM"，例如 "15:30"。
    """
    try:
        # 简单的时间格式校验
        datetime.datetime.strptime(time_str, "%H:%M")
        return f"✅ 成功为您设置 {time_str} 的【{reminder_type}】提醒。"
    except ValueError:
        return "错误：时间格式不正确，请使用 HH:MM 格式（如 14:30）。"