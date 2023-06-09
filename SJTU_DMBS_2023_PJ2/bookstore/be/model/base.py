"""Basic Connections and ORM definitions."""

import os
import logging
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Enum,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError


"""ORM Models definitions."""
Base = declarative_base()


ID_LEN = 256
PASSWD_LEN = 256
CODE_LEN = 512


class User(Base):
    __tablename__ = "User"

    id = Column(String(ID_LEN), primary_key=True, comment="user id")
    password = Column(String(PASSWD_LEN), nullable=False, comment="password")
    balance = Column(Integer, nullable=False, comment="the money")
    token = Column(String(CODE_LEN), comment="temporary token")
    terminal = Column(String(CODE_LEN), nullable=False, comment="device terminal code")


class Book(Base):
    __tablename__ = "Book"

    # two primary keys here
    id = Column(String(ID_LEN), primary_key=True, comment="book id")
    store_id = Column(
        String(ID_LEN), ForeignKey("Store.id"), primary_key=True, comment="store id"
    )
    stock_level = Column(
        Integer, nullable=False, comment="remains of the books in this store"
    )

    # book info
    title = Column(Text, nullable=False, index=True)
    author = Column(Text, nullable=False, index=True)
    publisher = Column(Text, nullable=False, index=True)
    original_title = Column(Text, nullable=False, index=True)
    translator = Column(Text, nullable=False, index=True)
    pub_year = Column(Text, nullable=False, index=True)
    pages = Column(Integer, nullable=False, index=True)
    price = Column(Integer, nullable=False, index=True)
    binding = Column(Text, nullable=False, index=True)
    isbn = Column(Text, nullable=False, index=True)
    currency_unit = Column(Text, nullable=False, index=True)

    # note: this columns are too large to create index
    tags = Column(Text, nullable=False)
    pictures = Column(Text, nullable=False)
    author_intro = Column(Text, nullable=False)
    book_intro = Column(Text, nullable=False)
    content = Column(Text, nullable=False)


class Store(Base):
    __tablename__ = "Store"

    id = Column(String(ID_LEN), primary_key=True, comment="store id")
    owner = Column(
        String(ID_LEN),
        ForeignKey("User.id"),
        nullable=False,
        comment="owner of the store",
    )


class Order(Base):
    __tablename__ = "Order"

    id = Column(String(ID_LEN), primary_key=True, comment="order id")
    buyer = Column(
        String(ID_LEN),
        ForeignKey("User.id", ondelete="SET NULL"),
        nullable=True,
        comment="buyer of the order",
    )
    store_id = Column(
        String(ID_LEN),
        ForeignKey("Store.id"),
        nullable=False,
        index=True,
        comment="store of the order",
    )
    total_price = Column(Integer, nullable=False, comment="total cost of the order")
    status = Column(
        Enum("unpaid", "paid", "delivered", "canceled", "finished", name="status"),
        nullable=False,
        comment="status of the order",
    )
    timestamp = Column(Float, nullable=False, comment="created time")


class OrderDetail(Base):
    __tablename__ = "OrderDetail"

    # two primary keys here
    order_id = Column(
        String(ID_LEN),
        ForeignKey("Order.id", ondelete="CASCADE"),
        primary_key=True,
        comment="order id",
    )
    # There is no unique constraint in book.id, so don't set it as ForeignKey.
    book_id = Column(String(ID_LEN), primary_key=True, comment="book id")
    count = Column(
        Integer, nullable=False, comment="the number of this book in the order"
    )
    price = Column(Integer, nullable=False, comment="the price of each book")


class SQLInstance:
    """Initialize SQL database and maintain the session."""

    def __init__(self, username, password, db_name):
        engine = create_engine(
            f"postgresql://{username}:{password}@localhost/{db_name}",
            echo=False,  # True,
            pool_size=64,
            pool_recycle=1800,
        )

        try:
            self.SessionMaker = sessionmaker(bind=engine)
            # init_tables
            Base.metadata.create_all(engine)
            logging.info("Create Table.")
        except SQLAlchemyError as e:
            logging.error(e)
            exit(0)


# global instance of database
db_instance: SQLInstance = None


def init_database(username, password, db_name):
    global db_instance
    db_instance = SQLInstance(username, password, db_name)


def get_session():
    global db_instance
    return db_instance.SessionMaker()
