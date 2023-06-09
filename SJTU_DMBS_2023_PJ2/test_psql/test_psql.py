import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, String, create_engine, Integer, Text, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import time

print(sqlalchemy.__version__)

engine = create_engine(
    "postgresql://postgres:123456@localhost/test",
    echo=True,
    pool_size=8,
    pool_recycle=1800,
)

print(engine)

DbSession = sessionmaker(bind=engine)
session = DbSession()

Base = declarative_base()


class User(Base):
    # 表的名字:
    __tablename__ = "users"

    # 表的结构:
    id = Column(
        Integer, autoincrement=True, primary_key=True, unique=True, nullable=False
    )
    name = Column(String(50), nullable=False)
    sex = Column(String(4), nullable=False)
    nation = Column(String(20), nullable=False)
    birth = Column(String(8), nullable=False)
    id_address = Column(Text, nullable=False)
    id_number = Column(String(18), nullable=False)
    creater = Column(String(32))
    create_time = Column(String(20), nullable=False)
    updater = Column(String(32))
    update_time = Column(
        String(20),
        nullable=False,
        default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        onupdate=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    )
    comment = Column(String(200))


def createTable():
    Base.metadata.create_all(engine)


createTable()
