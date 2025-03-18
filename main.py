from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from pydantic import BaseModel
import math

# Initialize FastAPI
app = FastAPI()

# Enable CORS for public access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Load dataset to get customer best send hours
df = pd.read_csv("updated_email_data.csv")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Define input model
class EmailData(BaseModel):
    customer_id: int

@app.get("/", response_class=HTMLResponse)
def serve_homepage(request: Request):
    """
    Serve the HTML page with a form for user input.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict-send-time/")
def predict_send_time(data: EmailData):
    """
    Predicts the best send time for a given customer ID.
    """
    customer_id = data.customer_id
    
    # Check if customer ID exists in the dataset
    if customer_id in df["customer_id"].values:
        best_hour = df.loc[df["customer_id"] == customer_id, "best_send_hour"].dropna().values
        times_used = df.loc[df["customer_id"] == customer_id, ["email_view_date_time", "cta_id1_click_datetime", "cta_id2_click_datetime"]].dropna(axis=1).values.flatten()
        times_used = [pd.to_datetime(t).strftime('%H:%M') for t in times_used]
        
        if len(best_hour) > 0:
            # Convert decimal hour to HH:MM format
            total_minutes = best_hour[0] * 60
            hours = math.floor(total_minutes // 60)
            minutes = round(total_minutes % 60)
            formatted_time = f"{hours:02d}:{minutes:02d}"
            
            return {"best_send_hour": formatted_time, "times_used": times_used}
        else:
            return JSONResponse(status_code=404, content={"error": "No engagement data available for this customer."})
    else:
        return JSONResponse(status_code=404, content={"error": "Customer ID not found."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
