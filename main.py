from fastapi import FastAPI, Body, File, UploadFile, HTTPException, Header
import pandas as pd
import io
import logging
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import Annotated, Any

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_SERVER_URL = "http://localhost:8005/api/v1/auth"


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    sheet_name: str = "Hourly Ville",
    Authorization: Annotated[str | None, Header()] = None,
    city: str = "",
):
    if not Authorization:
        raise HTTPException(status_code=403, detail="Missing authorization token")

    # Checking if the file is an Excel sheet
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File must be an Excel sheet")

    response = await validateToken(Authorization)
    if response["code"] != 200:
        raise HTTPException(status_code=401, detail="Token is invalid or Expired")
    try:
        content = await file.read()
        xl = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
        logging.info(f"Sheet Names: {xl.sheet_names}")

        # Validate sheet name
        if sheet_name not in xl.sheet_names:
            raise HTTPException(
                status_code=400,
                detail=f"Sheet '{sheet_name}' not found. Available sheets: {xl.sheet_names}",
            )

        data = pd.read_excel(
            io.BytesIO(content),
            engine="openpyxl",
            sheet_name=sheet_name,
            header=1,
            index_col=0,
        )
        logging.info(f"Data Preview:\n{data.head()}")

        # Fill NaN and replace infinite values
        data = data.fillna("").replace([float("inf"), float("-inf")], 0)

        return {"data": data.to_dict(orient="records")}

    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# Returns the sheets names and the cities in an excel file and
@app.post("/info")
async def getFileInfo(
    Authorization: Annotated[str | None, Header()] = None, file: UploadFile = File(...)
):

    if not Authorization:
        raise HTTPException(status_code=403, detail="Missing authorization token")

    # Checking if the file is an Excel sheet
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="File must be an Excel sheet")

    response = await validateToken(Authorization)
    if response["code"] != 200:
        raise HTTPException(status_code=401, detail="Token is invalid or Expired")

    try:
        content = await file.read()
        xl = pd.ExcelFile(
            io.BytesIO(content),
            engine='openpyxl'
        )
        
        df = pd.read_excel(
            io.BytesIO(content), 
            engine="openpyxl", 
            header=1, 
            index_col=0
        )
        
        cities = df['City'].values.tolist()
        uniqueCities = list(dict.fromkeys(cities))
        return {"sheets": xl.sheet_names, "cities": uniqueCities}

    except Exception as e:
        logging.error("Error processing file")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/validatetoken")
async def validateToken(Authorization: Annotated[str | None, Header()] = None):
    logging.info(Authorization)
    body = {"token": Authorization}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    response = requests.post(
        AUTH_SERVER_URL + "/validate-token", headers=headers, json=body
    )

    return {"code": response.json()["code"], "data": response.json()["data"]}


@app.post("/getsynthese")
async def getsynthese(
    Authorization: Annotated[str | None, Header()] = None,
    kpiData: dict[str, Any] = None,
    city: str = "",
):

    if not Authorization:
        raise HTTPException(status_code=403, detail="Missing authorization token")
    if not kpiData:
        raise HTTPException(status_code=400, detail="Missing data to calculate")
    response = await validateToken(Authorization)
    if response["code"] != 200:
        raise HTTPException(status_code=401, detail="Token is invalid or Expired")

    # @#Nbr_WCL_4G_CSSR<95%

    # ([CSSR]<95 And [Total Traffic (GB)]>0)

    nbr_wcl_4g_cssr = 0

    # @#Nbr_WCL_eDrop>1.5%

    # ([#Nbr_Drops]>50 And [ERAB Drop Rate]>1,5)

    nbr_wcl_edrop = 0

    # @#Nbr_WCL_DLThp

    # (([DL User Throughput (Mbps)]<3 And [earfcndl]InList(200; 1650; 2850)) Or ([DL User Throughput (Mbps)]<1 And [earfcndl]InList(1506; 6400))  And [Traffic DL (GB)]>=40 And [Cell Availability]>=99)

    nbr_wcl_dlthp = 0
    # @#Nbr_WCL_ULThp

    # (([UL User Throughput (Mbps)]<0,5 And [earfcndl]InList(200; 1650; 2850)) Or ([UL User Throughput (Mbps)]<0,2 And [earfcndl]InList(1506; 6400))  And [Traffic UL (GB)]>=7 And [Cell Availability Auto_Day]>=99)

    nbr_wcl_ulthp = 0

    # @#Nbr_WCL_DLPRB

    # [DL PRB Utilization]>70

    nbr_wcl_dlprb = 0
    # @#Nbr_WCL_Mobility_CSFB

    # ([CSFB_SR%]<90 And (attempts CSFB)>10)
    nbr_wcl_mobility_csfb = 0

    # @#Nbr_WCL_Volte_CSSR<95%

    # ([11_VOLTE eRAB SR%]<95 And [VoLTE_Erlang]>0)

    nbr_wcl_volte_cssr = 0

    # @#Nbr_WCL_Volte_DROP>1%

    # ([VoLTE_Drops]>2 And [VoLTE CDR%]>1)

    nbr_wcl_volte_drop = 0

    # @#Nbr_WCL_Volte_Intra<90%

    # ([Volte_IntraFreq_HOSR]<90 And (Attempts_IntraFreq QCI 1 >10))

    nbr_wcl_volte_intra = 0

    # @#Nbr_WCL_Volte_Inter<90%

    # ([Volte_InterFreq_HOSR]<90 And (Attempts_InterFQci1>10))
    nbr_wcl_volte_inter = 0

    # @#Nbr_WCL_SRVCC_SR<90%

    # ([13_SRVCC_WCDMA_SR_Tot]<90 And ([#Attempt_SRVCC_WCDMA])>10)

    nbr_wcl_srvcc_sr = 0

    # @#Nbr_WCL_Volte_Latency>35

    # ([Volte Latency]>35 And [VoLTE_Erlang]>0)

    nbr_wcl_volte_latency = 0

    return {"code": 200, "data": kpiData}
