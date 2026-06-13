"""
Webhook Receiver + PostgreSQL Query Demo
A simple webhook endpoint that receives SMS-style messages,
queries a PostgreSQL database for product info, and returns structured responses.
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import asyncpg
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Webhook & DB Integration Demo")

# --- Data Models ---

class IncomingMessage(BaseModel):
    sender: str
    text: str
    timestamp: Optional[str] = None


class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int


class StructuredResponse(BaseModel):
    sender: str
    original_text: str
    matched_product: Optional[Product] = None
    message: str


# --- Database Pool ---

DATABASE_URL = "postgresql://user:password@localhost:5432/products_db"
db_pool = None


async def get_pool():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return db_pool


# --- Webhook Endpoint ---

@app.post("/webhook/sms", response_model=StructuredResponse)
async def handle_webhook(msg: IncomingMessage):
    """
    Receives an SMS webhook, queries the product database,
    and returns a structured response with matching product info.
    """
    logger.info(f"Received webhook from {msg.sender}: {msg.text}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, price, stock
            FROM products
            WHERE name ILIKE $1
            LIMIT 1
            """,
            f"%{msg.text}%",
        )

    if rows:
        product = Product(
            id=rows[0]["id"],
            name=rows[0]["name"],
            price=float(rows[0]["price"]),
            stock=rows[0]["stock"],
        )
        response_text = (
            f"We found '{product.name}' - "
            f"${product.price:.2f}, {product.stock} in stock."
        )
    else:
        product = None
        response_text = f"Sorry, no product matching '{msg.text}' was found."

    return StructuredResponse(
        sender=msg.sender,
        original_text=msg.text,
        matched_product=product,
        message=response_text,
    )


# --- Health Check ---

@app.get("/health")
async def health():
    return {"status": "ok"}
