import pika, os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session

SQLALCHEMY_DATABASE_URL = 'DB_CONNECTION_URI_API_KEY'
RABBITMQ_URL = "RABBIT_CONNECTION_URI_API_KEY"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=900,
    pool_size=20,
    max_overflow=50
)

SessionFactory: Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    db = scoped_session(SessionFactory)()
    try:
        yield db
    finally:
        db.close()


def get_rabbitMQ_connection():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    return connection
