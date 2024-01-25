from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import Session, sessionmaker

url = URL.create(
    drivername="postgresql",
    username="postgres",
    password="postgres",
    host="localhost",
    database="siberian_invoices",
    port=5432,
)
engine = create_engine(url, echo=True)


class BaseService:
    """
    Базовый класс сервиса для связи с бд и получения сессии
    """

    def __init__(self, db_connection: Engine):
        self.db_connection = db_connection

    def get_session(self) -> Session:
        return sessionmaker(self.db_connection, autocommit=False, autoflush=False, class_=Session)()


def get_engine():
    return engine
