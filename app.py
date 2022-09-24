from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"message":"pong"}
