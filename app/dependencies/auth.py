import requests
from fastapi import HTTPException
from typing import Annotated

AUTH_SERVER_URL = "http://localhost:8005/api/v1/auth"

async def validate_token(Authorization: Annotated[str | None, None] = None):
    if not Authorization:
        raise HTTPException(status_code=403, detail="Missing authorization token")

    body = {"token": Authorization}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    response = requests.post(
        f"{AUTH_SERVER_URL}/validate-token", headers=headers, json=body
    )

    return {"code": response.json()["code"], "data": response.json()["data"]}