# Email Send Time Optimization API

This repository contains a FastAPI-based project designed to optimize email send times. The project analyzes historical email engagement data (including email view times and click times) to calculate the optimal send time(s) for each customer. It uses a combination of mean calculations and K-Means clustering to determine whether a single best time or multiple best times (for customers with widely varying engagement patterns) should be returned.

## Features

- **Data Processing:**  
  - Parses historical email data from a CSV file (`email_data.csv`).
  - Converts timestamp columns to datetime objects.
  - Extracts engagement hours in decimal format.

- **Optimal Time Calculation:**  
  - Computes the mean of engagement hours when times are closely clustered.
  - Applies K-Means clustering to detect multiple optimal times when engagement hours are spread apart (threshold > 3 hours).

- **API:**  
  - A FastAPI server that provides an endpoint to retrieve the optimal send time(s) for a given customer.
  - Detailed explanations of the calculation (mean and clustering details) are provided in the API response.

## Project Structure

- `email_data.csv`: Input CSV file with historical email data.
- `train_model.py`: Script that processes the CSV and creates `updated_email_data.csv` with optimal send times.
- `updated_email_data.csv`: Output CSV file with calculated optimal send times.
- `main.py`: FastAPI application that loads `updated_email_data.csv` and serves the API.
- `templates/index.html`: HTML file for the frontend UI to interact with the API.
- `README.md`: This file.

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- Pandas
- Scikit-Learn
- Pydantic

You can install the necessary packages using:

```bash
pip install fastapi uvicorn pandas scikit-learn pydantic
