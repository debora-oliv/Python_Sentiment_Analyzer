from config import settings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import redis

app = FastAPI(title="Analisador de Sentimentos")

cache = redis.Redis(host=settings.redis_host, port=6379, db=0)

class TextRequest(BaseModel):
    content: str

@app.post("/analyze")
async def analyze_text(request: TextRequest):
    if not request.content:
        raise HTTPException(status_code=400, detail="Conteúdo não pode estar vazio.")

    dados_job = json.dumps({"text": request.content})

    cache.rpush('sentiments_queue', dados_job)
    
    return {"message": "Texto enviado para processamento!", "status": "queued"}

@app.get("/")
def read_root():
    return {"API funcionando! | user_db": settings.postgres_user}