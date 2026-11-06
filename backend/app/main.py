from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.models.recipe import Recipe
from app.core.config import settings
from app.core.database import engine, get_db
from app.models.user_profile import Base, UserProfile
from app.models.chat_history import ChatHistory
from app.agent.graph import fitmate_app, llm
from app.agent.prompts import SYSTEM_PROMPT, MEMORY_PROMPT_TEMPLATE
from fastapi.responses import StreamingResponse
from app.models.weight_log import WeightLog
from datetime import datetime
from app.models.diet_log import DietLog
from datetime import date
import json
import os
import re

Base.metadata.create_all(bind=engine)
USER_FILE = "users.json"
app = FastAPI(title="FitMate Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str
    message: str
    history: List[dict] = []

class ChatResponse(BaseModel):
    reply: str

class DietLogRequest(BaseModel):
    user_id: str
    food_name: str
    calories: int
    meal_type: str = "加餐"
# ==========================================
# 后台任务：自动记忆提取
# ==========================================
def extract_and_save_memory(user_id: str, user_message: str, db: Session):
    """
    静默运行：让大模型分析用户的话，提取长期记忆。
    """
    # 1. 让 LLM 提取 JSON 格式的记忆
    extraction_prompt = f"""
    分析用户的话，提取需要长期记住的个人信息（身高、体重、过敏史、伤病）。
    只返回纯 JSON 格式，如果没有提到任何信息，返回空 JSON {{}}。
    用户说：“{user_message}”
    
    例如：
    输出格式：{{"height_cm": 175, "weight_kg": 80, "allergy": "花生", "injury": "腰伤"}}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=extraction_prompt)])
        content = response.content.strip()
        # 清理大模型可能返回的 Markdown 代码块符号
        if content.startswith("```json"):
            content = content[7:-3]
            
        memory_data = json.loads(content)
        
        # 2. 如果提取到了数据，更新数据库
        if memory_data:
            profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if not profile:
                profile = UserProfile(user_id=user_id)
                db.add(profile)
            
            if "height_cm" in memory_data and memory_data["height_cm"]:
                profile.height_cm = float(memory_data["height_cm"])
            if "weight_kg" in memory_data and memory_data["weight_kg"]:
                profile.weight_kg = float(memory_data["weight_kg"])
            if "allergy" in memory_data and memory_data["allergy"]:
                profile.allergy = str(memory_data["allergy"])
            if "gender" in memory_data and memory_data["gender"]:
                profile.gender = str(memory_data["gender"])
            if "injury" in memory_data and memory_data["injury"]:
                profile.injury = str(memory_data["injury"])
            if "age" in memory_data and memory_data["age"]:
                profile.age = int(memory_data["age"])
            
            db.commit()
            print(f"🧠 [后台] 成功提取并更新了用户 {user_id} 的长期记忆: {memory_data}")
    except Exception as e:
        print(f"⚠️ [后台] 记忆提取失败 (不影响正常对话): {e}")

# ==========================================
# 聊天主接口
# ==========================================
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        messages = []
        
        # 1. 查库，拼接长期记忆
        profile = db.query(UserProfile).filter(UserProfile.user_id == request.user_id).first()
        system_content = SYSTEM_PROMPT
        
        if profile:
            memory_text = MEMORY_PROMPT_TEMPLATE.format(
                height=profile.height_cm or "未记录",
                weight=profile.weight_kg or "未记录",
                allergy=profile.allergy or "无"
            )
            system_content += memory_text
            
        messages.append(SystemMessage(content=system_content))

        # 2. 恢复短期记忆
        for msg in request.history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
                
        # 3. 当前输入
        messages.append(HumanMessage(content=request.message))
        
        # 4. 运行 Agent
        events = fitmate_app.stream({"messages": messages}, stream_mode="values")
        
        final_reply = ""
        for event in events:
            last_msg = event["messages"][-1]
            if last_msg.type == "ai" and last_msg.content:
                final_reply = last_msg.content
                
        # ==========================================
        # 5. 数据库操作：保存记录 + 触发自动记忆提取
        # ==========================================
        # 保存用户消息
        db.add(ChatHistory(user_id=request.user_id, role="user", content=request.message))
        # 保存 AI 回复
        db.add(ChatHistory(user_id=request.user_id, role="assistant", content=final_reply))
        db.commit()
        
        # 触发自动记忆
        extract_and_save_memory(request.user_id, request.message, db)

        return {"reply": final_reply}
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# ==========================================
# 流式对话接口
# ==========================================
@app.post("/api/chat_stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        messages = []
        
        # 1. 查库，拼接长期记忆
        profile = db.query(UserProfile).filter(UserProfile.user_id == request.user_id).first()
        system_content = SYSTEM_PROMPT
        
        if profile:
            memory_text = MEMORY_PROMPT_TEMPLATE.format(
                height=profile.height_cm or "未记录",
                weight=profile.weight_kg or "未记录",
                allergy=profile.allergy or "无"
            )
            system_content += memory_text
            
        # ==========================================
        # 把当前时间和格式要求告诉大模型
        # ==========================================
        system_content += (
            f"\n【当前系统时间】：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}。"
            "\n【严格指令】：如果用户让你设置提醒，请务必把时间转换为标准的 24 小时制 HH:MM 格式（例如：09:30）。"
            "\n【饮食记录指令】：如果用户提到吃了什么/让你记录饮食，你在回复的最后必须附带一行不可见的 JSON 格式数据，包含核心食物名称和总热量。格式：`[DIET_LOG: {\"food_name\": \"米饭+鸡肉\", \"calories\": 432, \"meal_type\": \"晚餐\"}]`。请严格填入核心食物名称（不要带任何动词）， calories 填你算出的最后总计数值（纯数字，不要范围）。"
        )
        # ==========================================
            
        messages.append(SystemMessage(content=system_content))

        # 2. 恢复短期记忆
        for msg in request.history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
                
        # 3. 当前输入
        messages.append(HumanMessage(content=request.message))
        
        # 4. 定义一个生成器，用于流式返回
        async def generate():
            # 因为大模型调工具不是流式的，我们需要分两步：
            # 第一轮：让 Agent 跑一遍（如果没有工具调用，这里会生成完整回复）
            # 注意：这里调用 astream_events 或直接 invoke 判断是否调用了工具
            # 为了简化，我们先把整个 Agent 跑完（如果调了工具它会自动处理）
            events = fitmate_app.stream({"messages": messages}, stream_mode="values")
            final_reply = ""
            for event in events:
                last_msg = event["messages"][-1]
                if last_msg.type == "ai" and last_msg.content:
                    final_reply = last_msg.content
            
            # 拿到最终结果后，我们模拟打字机效果，一个字一个字推给前端
        
            for char in final_reply:
                yield char
                import asyncio
                await asyncio.sleep(0.02) # 控制打字速度，0.02秒一个字
            calorie_match = re.search(r'约?\s*(\d+)\s*(?:卡|大卡)', final_reply)
            if calorie_match and ("记录" in final_reply or "打卡" in final_reply):
                calories = int(calorie_match.group(1))
                # 提取食物名
                new_diet = DietLog(user_id=request.user_id, food_name=request.message, calories=calories)
                db.add(new_diet)
                db.commit()
                print(f"✅ AI 自动帮用户记录了饮食: {request.message} - {calories}卡")    

        # 5. 保存历史记录（在流式输出前保存，或者后台保存）
        # 这里简单起见，我们先在流开始前把用户消息存了
        db.add(ChatHistory(user_id=request.user_id, role="user", content=request.message))
        db.commit()
        
        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/profile/{user_id}")
def get_profile(user_id: str, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@app.post("/api/profile/{user_id}")
def update_profile(
    user_id: str, 
    height_cm: float = None, 
    weight_kg: float = None, 
    age: int = None, 
    gender: str = None, 
    allergy: str = None, 
    injury: str = None, 
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
    
    # === 如果传了体重，并且和旧体重不一样，存入历史记录 ===
    if weight_kg is not None:
        if profile.weight_kg != weight_kg:
            new_log = WeightLog(user_id=user_id, weight_kg=weight_kg)
            db.add(new_log)
        profile.weight_kg = weight_kg
    # ========================================================

    if height_cm is not None: profile.height_cm = height_cm
    if age is not None: profile.age = age
    if gender is not None: profile.gender = gender
    if allergy is not None: profile.allergy = allergy
    if injury is not None: profile.injury = injury
    
    db.commit()
    db.refresh(profile)
    return profile

# ==========================================
# 账号体系：注册与登录（基于本地 JSON 文件）
# ==========================================
class AuthRequest(BaseModel):
    username: str
    password: str

# 读取本地用户文件
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 保存到本地用户文件
def save_users(users_data):
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

# 注册接口
@app.post("/api/register")
def register(req: AuthRequest):
    users = load_users()
    if req.username in users:
        raise HTTPException(status_code=400, detail="该用户名已被注册，请换一个")
    
    # 保存新用户
    users[req.username] = req.password
    save_users(users)
    return {"status": "success", "message": "注册成功，请前往登录"}

# 登录接口
@app.post("/api/login")
def login(req: AuthRequest):
    users = load_users()
    if req.username not in users:
        raise HTTPException(status_code=400, detail="用户不存在，请先注册")
    
    if users[req.username] != req.password:
        raise HTTPException(status_code=400, detail="密码错误，请重试")
        
    return {"status": "success", "message": "登录成功"}
class RecipeCreate(BaseModel):
    title: str
    calories: int
    description: str

@app.get("/api/recipes")
def get_recipes(db: Session = Depends(get_db)):
    # 获取数据库里的食谱，如果没有，就返回空列表
    return db.query(Recipe).all()

@app.post("/api/recipes")
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    new_recipe = Recipe(
        title=recipe.title, 
        calories=recipe.calories, 
        description=recipe.description
    )
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe
@app.delete("/api/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="食谱不存在")
    db.delete(recipe)
    db.commit()
    return {"message": "删除成功"}
@app.get("/api/weight_history/{user_id}")
def get_weight_history(user_id: str, db: Session = Depends(get_db)):
    # 查最近 10 条记录，按时间正序排
    logs = db.query(WeightLog).filter(WeightLog.user_id == user_id).order_by(WeightLog.recorded_at.asc()).limit(20).all()
    return [{
        "date": log.recorded_at.strftime("%m-%d %H:%M"), 
        "weight": log.weight_kg} for log in logs]
@app.post("/api/diet_logs")
def add_diet_log(req: DietLogRequest, db: Session = Depends(get_db)):
    log = DietLog(
        user_id=req.user_id, 
        food_name=req.food_name, 
        calories=req.calories, 
        meal_type=req.meal_type
    )
    db.add(log)
    db.commit()
    return {"status": "success", "message": "记录成功"}

@app.get("/api/diet_logs/{user_id}")
def get_today_diet_logs(user_id: str, db: Session = Depends(get_db)):
    # 查今天该用户的所有记录
    today = date.today()
    logs = db.query(DietLog).filter(
        DietLog.user_id == user_id,
        DietLog.recorded_at >= today
    ).order_by(DietLog.recorded_at.desc()).all()
    return logs

@app.post("/api/diet_logs")
def add_diet_log(req: DietLogRequest, db: Session = Depends(get_db)):
    try:
        new_log = DietLog(
            user_id=req.user_id, 
            food_name=req.food_name, 
            calories=int(req.calories), 
            meal_type=req.meal_type
        )
        db.add(new_log)
        db.commit()
        return {"status": "success", "message": "记录成功"}
    except Exception as e:
        print(f"❌ 报错: {e}")
        raise HTTPException(status_code=500, detail=str(e))