# Webhook & Database Integration Demo

A Python FastAPI application that receives SMS webhooks, queries a PostgreSQL database for product information, and returns structured response messages.

## Features

- FastAPI webhook endpoint (POST /webhook/sms)
- Async PostgreSQL querying via asyncpg
- Structured JSON responses with matched product data
- Input validation with Pydantic models
- Logging and error handling

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

## API

- `POST /webhook/sms` — Receive a text message and return matching product info
- `GET /health` — Health check
