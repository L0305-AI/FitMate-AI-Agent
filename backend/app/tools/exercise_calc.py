from langchain_core.tools import tool

@tool
def calculate_health_metrics(weight_kg: float, height_cm: float, age: int, gender: str) -> str:
    """
    计算用户的 BMI 和基础代谢率 (BMR)。
    参数:
    weight_kg: 体重，单位公斤。
    height_cm: 身高，单位厘米。
    age: 年龄。
    gender: 性别，填 "male" 或 "female"。
    """
    # 💡工具异常处理
    try:
        if weight_kg <= 0 or weight_kg > 300:
            return "错误：体重输入不合理，请输入 0-300 之间的数字。"
        if height_cm <= 0 or height_cm > 250:
            return "错误：身高输入不合理，请输入 0-250 之间的数字。"
            
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        # Mifflin-St Jeor 公式计算 BMR
        if gender.lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
            
        # 判定 BMI 状态
        if bmi < 18.5:
            status = "偏瘦"
        elif 18.5 <= bmi < 24:
            status = "正常"
        elif 24 <= bmi < 28:
            status = "超重"
        else:
            status = "肥胖"
            
        return f"计算结果：BMI为 {bmi:.1f} ({status})，基础代谢率(BMR)约为 {bmr:.0f} 千卡/天。"
        
    except Exception as e:
        # 任何不可预见的错误，都兜底返回，不让系统崩溃
        return f"计算工具发生异常，请检查输入格式。错误信息：{str(e)}"