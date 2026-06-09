import os

import psycopg2
import redis
from flask import Flask

app = Flask(__name__)


def get_postgres_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "app_db"),
        user=os.getenv("POSTGRES_USER", "app_user"),
        password=os.getenv("POSTGRES_PASSWORD", "app_password"),
    )


def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


def init_db():
    connection = get_postgres_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    connection.commit()
    cursor.close()
    connection.close()


@app.route("/")
def home():
    # PostgreSQL part
    connection = get_postgres_connection()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO visits DEFAULT VALUES;")
    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM visits;")
    postgres_visits = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    # Redis part
    redis_client = get_redis_client()
    redis_visits = redis_client.incr("redis_visits")
    redis_client.set("last_postgres_count", postgres_visits)

    return (
        f"Hello from Docker! "
        f"PostgreSQL visits: {postgres_visits}, "
        f"Redis visits: {redis_visits}"
    )


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/redis")
def redis_status():
    redis_client = get_redis_client()

    return {
        "redis_status": "ok",
        "redis_visits": redis_client.get("redis_visits"),
        "last_postgres_count": redis_client.get("last_postgres_count"),
    }


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000)