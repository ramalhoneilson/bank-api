from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.config.config import DATABASE_URL, ENVIRONMENT

print(f"Connecting to database: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
