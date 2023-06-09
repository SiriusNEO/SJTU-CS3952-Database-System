"""Seller related APIs."""

from typing import Tuple

import logging
from be.model import error
from be.model.base import get_session, Book, Store, Order
from be.model.utils import (
    user_id_exists,
    store_id_exists,
    book_id_exists,
    serialize_dict,
)

from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class SellerAPI:
    """Backend APIs related to seller manipulation."""

    @staticmethod
    def add_book(
        user_id: str,
        store_id: str,
        book_id: str,
        book_info: dict,
        stock_level: int,
    ) -> Tuple[int, str]:
        """Add a book to a store.

        Parameters
        ----------
        user_id : str
            The user_id of the seller.

        store_id : str
            The store_id of the store.

        book_id : str
            The book_id of the book.

        book_info : dict
            The book info dict.

        stock_level : int
            The stock_level of the book in this store.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            if not user_id_exists(user_id):
                return error.error_non_exist_user_id(user_id)
            if not store_id_exists(store_id):
                return error.error_non_exist_store_id(store_id)

            session = get_session()
            assert book_info.pop("id") == book_id
            book_info = serialize_dict(book_info)
            # print("BI: ", book_info["title"])
            book = Book(
                id=book_id, store_id=store_id, stock_level=stock_level, **book_info
            )
            session.add(book)
            session.commit()
            session.close()

        except IntegrityError:
            return error.error_exist_book_id(book_id)
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            session.rollback()
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def add_stock_level(
        user_id: str, store_id: str, book_id: str, add_stock_level: int
    ) -> Tuple[int, str]:
        """Add the stock_level of a book in a store.

        Parameters
        ----------
        user_id : str
            The user_id of the seller.

        store_id : str
            The store_id of the store.

        book_id : str
            The book_id of the book.

        add_stock_level : int
            The stock_level of the book to be added.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            if not user_id_exists(user_id):
                return error.error_non_exist_user_id(user_id)
            if not store_id_exists(store_id):
                return error.error_non_exist_store_id(store_id)
            if not book_id_exists(book_id):
                return error.error_non_exist_book_id(book_id)

            session = get_session()
            session.query(Book).filter_by(id=book_id, store_id=store_id).update(
                {
                    "stock_level": Book.stock_level + add_stock_level,
                },
            )
            session.commit()
            session.close()

        except IntegrityError:
            return error.error_non_exist_book_id(book_id)
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            session.rollback()
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def create_store(user_id: str, store_id: str) -> Tuple[int, str]:
        """A user create a store.

        Parameters
        ----------
        user_id : str
            The user_id of the creator.

        store_id : str
            The store_id of the created store.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            if not user_id_exists(user_id):
                return error.error_non_exist_user_id(user_id)

            session = get_session()
            store = Store(id=store_id, owner=user_id)
            session.add(store)
            session.commit()
            session.close()

        except IntegrityError:
            return error.error_exist_store_id(store_id)
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            session.rollback()
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def mark_order_shipped(store_id: str, order_id: str) -> Tuple[int, str]:
        """The seller marks an order as shipped.

        Parameters
        ----------
        store_id : str
            The store_id of the order.

        order_id : str
            The shipped order.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            if not store_id_exists(store_id):
                return error.error_non_exist_store_id(store_id)

            session = get_session()
            cursor = session.query(Order).filter(Order.id == order_id)
            result = cursor.first()

            if result is None:
                session.close()
                return error.error_non_exist_order_id(order_id)

            if result.status != "paid":
                session.close()
                return error.error_order_status(result.status)

            if result.store_id != store_id:
                session.close()
                return error.error_store_id_match(result.store_id, store_id)

            # update the order status
            cursor.update({"status": "delivered"})
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            session.rollback()
            return 530, "{}".format(str(e))

        return 200, "ok"
