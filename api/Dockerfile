FROM python:3.11-slim

WORKDIR /app

# Instala dependências primeiro para otimização de cache
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py .
COPY api/ .

EXPOSE 8000

# uvicorn main:app roda a aplicação
# --reload inicia com recarregamento automático
# --host 0.0.0.0 --port 8000 define host e porta
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]