## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/watch` | Return the message log |
| GET | `/json` | Return the save/load model as JSON |
| POST | `/addproduct` | Seed a test product (PostgreSQL + cache invalidation) |
| GET | `/getproducts` | List products (Redis cache-aside, falls back to PostgreSQL) |
| GET | `/health` | Health check (validates connection settings) |
| GET | `/postgres` | PostgreSQL version probe |
| GET | `/mongo` | MongoDB version probe |
| GET | `/sqlite` | SQLite version probe |

## Run with Docker

```bash
cp .env.example .env
# edit .env with your values
docker-compose up --build
```

## Run locally

```bash
cp .env.example .env
# edit .env with your values
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Notes

- SQLite connection string defaults to `data/default.db` (relative to working directory).
- Redis is optional; when `REDIS_CONNECTION` is not set, cache operations are no-ops.