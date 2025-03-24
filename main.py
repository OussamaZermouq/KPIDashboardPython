from fastapi import FastAPI, File, UploadFile, HTTPException
import pandas as pd
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), sheet_name: str = "Hourly Ville"):
    # Checking if the file is an Excel sheet
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File must be an Excel sheet")
    
    try:
        content = await file.read()
        xl = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
        logging.info(f"Sheet Names: {xl.sheet_names}")

        # Validate sheet name
        if sheet_name not in xl.sheet_names:
            raise HTTPException(
                status_code=400, 
                detail=f"Sheet '{sheet_name}' not found. Available sheets: {xl.sheet_names}"
            )
        
        # Read the specific sheet with header row (assumed to be row 1)
        data = pd.read_excel(io.BytesIO(content), engine="openpyxl", sheet_name=sheet_name, header=1)
        logging.info(f"Data Preview:\n{data.head()}")

        # Rename columns: If column name is NaN or starts with "Unnamed"
        data.columns = [f"Column_{i}" if pd.isna(col) or str(col).startswith("Unnamed") else col for i, col in enumerate(data.columns)]
        
        # Fill NaN and replace infinite values
        data = data.fillna("").replace([float("inf"), float("-inf")], 0)
        
        return {"data": data.to_dict(orient="records")}
    
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
