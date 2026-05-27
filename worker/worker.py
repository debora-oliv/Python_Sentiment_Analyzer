from config import settings
from textblob import TextBlob
import redis
import psycopg2
import json
import time

def get_db_connection():
    while True:
        try:
            conn = psycopg2.connect(
                host=settings.db_host,
                database=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password
            )
            return conn
        except Exception as e:
            print(f"Erro: {e}. Aguardando conexão com o banco...")
            time.sleep(2)

def process_queue():
    print("Worker iniciado e conectado!")

    r = redis.Redis(host=settings.redis_host, port=6379, db=0)
    conn = get_db_connection()
    cur = conn.cursor()

    while True:
        try:
            _, message = r.blpop('sentiments_queue')
            data = json.loads(message)
            text = data.get("text")

            analysis = TextBlob(text)
            score = analysis.sentiment.polarity

            if score > 0:
                label = "Positivo"
            elif score < 0:
                label = "Negativo"
            else:
                label = "Neutro"

            cur.execute(
                "INSERT INTO sentiments (text_content, score, label) VALUES (%s, %s, %s)",
                (text, score, label)
            )
            conn.commit()

            print(f"[PROCESSADO] Texto: '{text[:30]}...' -> {label} (Salvo no Banco)")

        except Exception as e:
            print(f"Erro ao processar item: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
            if conn.closed:
                cur.close()
                conn = get_db_connection()
                cur = conn.cursor()

if __name__ == "__main__":
    process_queue()