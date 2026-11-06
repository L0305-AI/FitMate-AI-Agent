from langchain_core.tools import tool

@tool
def calculate_food_calories(food_name: str, amount_grams: float) -> str:
    """
    查询指定食物的热量，并计算指定克数的总热量。
    """
    try:
        if amount_grams <= 0:
            return "错误：食物重量必须大于0。"
            
        # 简易本地食物热量库 (千卡/100克)，可扩充
        food_db = {
            "米饭": 116, "馒头": 223, "面条": 286,
            "鸡胸肉": 133, "牛肉": 125, "鸡蛋": 144,
            "苹果": 54, "香蕉": 93, "牛奶": 54
        }
        
        # 模糊匹配
        matched_food = None
        for k in food_db.keys():
            if k in food_name:
                matched_food = k
                break
                
        if not matched_food:
            return f"抱歉，本地热量库暂未收录【{food_name}】，请换一种常见食物。"
            
        per_100g = food_db[matched_food]
        total_cal = (per_100g / 100) * amount_grams
        
        return f"{amount_grams}克{matched_food}的总热量约为 {total_cal:.1f} 千卡。"
        
    except Exception as e:
        return f"热量计算工具异常：{str(e)}"