from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from pydantic import BaseModel
import math
import ast

app = FastAPI()

# Load the updated dataset
df = pd.read_csv("updated_email_data.csv")

# Parse the best_send_hours column from string to a Python list
def parse_list(value):
    try:
        return ast.literal_eval(value) if isinstance(value, str) else value
    except (SyntaxError, ValueError):
        return []

df["best_send_hours"] = df["best_send_hours"].apply(parse_list)

templates = Jinja2Templates(directory="templates")

class EmailData(BaseModel):
    customer_id: int

@app.get("/", response_class=HTMLResponse)
def serve_homepage(request: Request):
    """Serve the HTML page with a form for user input."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict-send-time/")
def predict_send_time(data: EmailData):
    """
    For a given customer ID:
      - If engagement data exists, convert the best send time(s) from decimal to HH:MM.
      - Provide a step-by-step explanation.
      - If no data, return an error message.
    """
    customer_id = data.customer_id

    if customer_id not in df["customer_id"].values:
        return JSONResponse(status_code=404, content={"error": "Customer ID not found."})

    row = df.loc[df["customer_id"] == customer_id]
    best_hours_arr = row["best_send_hours"].dropna().values
    # Get raw engagement times used (for formula display)
    raw_times = row[["email_view_date_time", "cta_id1_click_datetime", "cta_id2_click_datetime"]].dropna(axis=1).values.flatten()
    times_used = [pd.to_datetime(t).strftime('%H:%M') for t in raw_times]

    if len(best_hours_arr) > 0 and isinstance(best_hours_arr[0], list) and len(best_hours_arr[0]) > 0:
        decimal_times = best_hours_arr[0]  # This is a list of floats (e.g., [20.33])
        optimal_times = []
        for dec in decimal_times:
            total_minutes = dec * 60
            hh = math.floor(total_minutes // 60)
            mm = round(total_minutes % 60)
            optimal_times.append(f"{hh:02d}:{mm:02d}")

        # Explain formula:
        if len(decimal_times) == 1:
            formula_explain = "Only one data point or cluster => Mean Calculation (no clustering applied)"
            step_calc = f"Mean Time: {optimal_times[0]}"
        else:
            separation = abs(decimal_times[-1] - decimal_times[0])
            if separation > 3:
                formula_explain = "Data separated by >3 hours => K-Means Clustering used to return two distinct times"
            else:
                formula_explain = "Data not far apart => Mean Calculation used"
            mean_val = round(sum(decimal_times)/len(decimal_times), 2)
            step_calc = f"Mean: {mean_val}; Derived Time: {optimal_times}"

        return {
            "best_send_times": optimal_times,
            "formula": formula_explain,
            "calculation": step_calc,
            "times_used": times_used
        }
    else:
        return JSONResponse(
            status_code=404,
            content={"error": "Sorry, we don't have enough data to determine optimal send times."}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
