from sqlalchemy import text
from app.db.session import SessionLocal

db = SessionLocal()
rows = db.execute(
    text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
)
print([r[0] for r in rows])
db.close()
