from .exercise_calc import calculate_health_metrics
from .diet_calc import calculate_food_calories
from .reminder import set_health_reminder

# 导出所有工具，方便 Agent 导入
all_tools = [
    calculate_health_metrics,
    calculate_food_calories,
    set_health_reminder
]