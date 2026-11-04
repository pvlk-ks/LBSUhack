from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="LBSUhack Core API")

class BusinessModel(BaseModel):
    investments: float
    monthly_revenue: float
    monthly_expenses: float
    
@app.get("/")
def check_status():
    return {"status": "Beckend is running"}

@app.post("/app/v1/calculate")
def calculate(data: BusinessModel):
    
    monthly_profit = data.monthly_revenue - data.monthly_expenses
    years = ["Year 1", "Year 2", "Year 3"]
    timeline = []
    current_balance = -data.investments
    
    for year in years:
        current_balance += monthly_profit * 12
        timeline.append({
            "Timeline": year,
            "Net_Profit": round(current_balance, 2)
        })
        
    return{
        "status": "success",
        "result": timeline
    }