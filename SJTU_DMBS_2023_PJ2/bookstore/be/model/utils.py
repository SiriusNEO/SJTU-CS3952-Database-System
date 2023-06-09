import time
import json

from sqlalchemy import exists
from be.model.base import get_session, User, Book, Order, Store

ORDER_EXPIRED_TIME_INTERVAL = 10


def check_expired(timestamp: float) -> bool:
    """Check whether an order is expired."""

    if time.time() - timestamp > ORDER_EXPIRED_TIME_INTERVAL:
        return True
    return False


def to_dict(model):
    """ORM Model -> dict"""
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}


def serialize_dict(data_dict):
    for key in data_dict:
        if not isinstance(data_dict[key], str) and not isinstance(data_dict[key], int):
            data_dict[key] = json.dumps(data_dict[key])
    return data_dict


"""APIs to check id existence."""


def user_id_exists(user_id: str) -> bool:
    session = get_session()
    is_exists = session.query(exists().where(User.id == user_id)).scalar()
    session.close()
    return is_exists


def store_id_exists(store_id: str) -> bool:
    session = get_session()
    is_exists = session.query(exists().where(Store.id == store_id)).scalar()
    session.close()
    return is_exists


def order_id_exists(order_id: str) -> bool:
    session = get_session()
    is_exists = session.query(exists().where(Order.id == order_id)).scalar()
    session.close()
    return is_exists


def book_id_exists(book_id: str) -> bool:
    session = get_session()
    is_exists = session.query(exists().where(Book.id == book_id)).scalar()
    session.close()
    return is_exists
