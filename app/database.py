from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_HOST=os.getenv("DATABASE_HOST")
DATABASE_USERNAME=os.getenv("DATABASE_USERNAME")
DATABASE_PORT=os.getenv("DATABASE_PORT")
DATABASE_NAME=os.getenv("DATABASE_NAME")
DATABASE_PASSWORD=os.getenv("DATABASE_PASSWORD")


DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


with engine.connect() as connection:
    print("Database Connected Successfully")


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()