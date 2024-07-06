import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# DB_STRING = f'sqlite:///db.db'
DB_STRING = f'postgresql+psycopg2://postgres:example@{os.environ.get("DB_HOST", "localhost")}:5432'

engine = create_engine(DB_STRING, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db_session = scoped_session(SessionLocal)

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)


def shutdown_session(exception=None):
    db_session.remove()
