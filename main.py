from fastapi import FastAPI, File, UploadFile, HTTPException
import pandas as pd
import io
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
origins= [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
        
        data = pd.read_excel(io.BytesIO(content), engine="openpyxl", sheet_name=sheet_name, header=1, index_col=0)
        logging.info(f"Data Preview:\n{data.head()}")

        
        # Fill NaN and replace infinite values
        data = data.fillna("").replace([float("inf"), float("-inf")], 0)
        
        return {"data": data.to_dict(orient="records")}
    
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/sheets")
async def getSheetNames(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File must be an Excel sheet")
    
    try:
        content = await file.read()
        xl = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
        logging.info(f"Sheet Names: {xl.sheet_names}")
        return {"data": xl.sheet_names}

    except Exception as e:
        logging.error("Error processing file")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
        
    