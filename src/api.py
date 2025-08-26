from fastapi import FastAPI
from pydantic import BaseModel
from src.agent import WaterIntakeAgent
from src.database import log_intake, get_intake_history
# Assume you have a logger module
from src.logger import log_message

app = FastAPI()
agent = WaterIntakeAgent()

class WaterIntakeRequest(BaseModel):
    user_id: str
    intake_ml: float  # float is better for ml input

@app.post("/log_intake")
async def log_water_intake(request: WaterIntakeRequest):
    log_intake(request.user_id, request.intake_ml)
    # Convert ml to liters for AI analysis
    liters = request.intake_ml / 1000
    analysis = agent.analyze_intake(liters)
    log_message(f"user {request.user_id} logged {request.intake_ml} ml")
    return {"message": "Water intake logged successfully", "analysis": analysis}

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    history = get_intake_history(user_id)
    return {"user_id": user_id, "history": history}
