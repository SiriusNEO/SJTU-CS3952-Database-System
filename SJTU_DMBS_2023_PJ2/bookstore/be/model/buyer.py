"""Buyer related APIs."""

from typing import List, Tuple

import time
import uuid

import logging
from be.model import error
from be.model.base import get_session, Book, User, Order, Store, OrderDetail

from sqlalchemy.exc import SQLAlchemyError
from be.model.utils import check_expired, user_id_exists, store_id_exists, to_dict


class BuyerAPI:
    """Backend APIs related to buyer manipulation."""

    @staticmethod
    def new_order(
        user_id: str,
        store_id: str,
        books: List[Tuple[str, int]],
    ) -> Tuple[int, str, str]:
        """Create an order to a store.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        store_id : str
            The store_id of the store.

        books : List[str, int]
            The books to be bought. A list of (book_id: str, count: int).

        Returns
        -------
        (code : int, msg : str, order_id : str)
            The return status. Note that it will return the corresponding order_id.
        """
        try:
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            total_price = 0
            order_id = uid

            if not user_id_exists(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not store_id_exists(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)

            session = get_session()
            books_data = []

            for book_id, count in books:
                cursor = session.query(Book).filter_by(id=book_id, store_id=store_id)
                result = cursor.first()

                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = result.stock_level
                price = result.price

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor.update({"stock_level": Book.stock_level - count})

                total_price += count * price
                books_data.append([book_id, count, price])

            now_time = time.time()
            order = Order(
                id=order_id,
                buyer=user_id,
                store_id=store_id,
                total_price=total_price,
                status="unpaid",
                timestamp=now_time,
            )
            session.add(order)

            for book_id, count, price in books_data:
                order_data_book = OrderDetail(
                    order_id=order_id,
                    book_id=book_id,
                    count=count,
                    price=price,
                )
                session.add(order_data_book)

            session.commit()
            session.close()
        except SQLAlchemyError as e:
            logging.info("528, {}".format(str(e)))
            session.rollback()
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            session.rollback()
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    @staticmethod
    def payment(user_id: str, password: str, order_id: str) -> Tuple[int, str]:
        """The buyer pay for an order.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        password : str
            The password of the buyer account.

        order_id : str
            The order the buyer pay for.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            # Part 1. Get the order info.
            session = get_session()

            result = session.query(Order).filter(Order.id == order_id).first()
            if result is None:
                return error.error_non_exist_order_id(order_id)

            if result.status != "unpaid":
                session.close()
                return error.error_order_status(result.status)

            if result.buyer is None:
                session.close()
                return error.error_non_exist_user_id(user_id)

            if result.buyer != user_id:
                session.close()
                return error.error_authorization_fail()

            if check_expired(result.timestamp):
                code, message = BuyerAPI.cancel_order(user_id, password, order_id)
                if code != 200:
                    return code, message
                session.close()
                return error.error_order_status("canceled")

            total_price = result.total_price

            # Part 2. Get the user info and update the buyer balance.
            cursor = session.query(User).filter(User.id == user_id)
            result = cursor.first()
            if result is None:
                session.close()
                return error.error_non_exist_user_id(user_id)

            if password != result.password:
                session.close()
                return error.error_authorization_fail()

            balance = result.balance

            if balance < total_price:
                session.close()
                return error.error_not_sufficient_funds(order_id)

            # buyer's balance -= total_price
            cursor.update({"balance": User.balance - total_price})

            # Part 3. Update the order status.
            session.query(Order).filter(Order.id == order_id).update({"status": "paid"})
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            logging.error(e)
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(e)
            session.rollback()
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def add_funds(user_id: str, password: str, add_value: int) -> Tuple[int, str]:
        """Add funds for an account.

        Parameters
        ----------
        user_id : str
            The user_id of the account.

        password : str
            The password of the account.

        add_value : int
            The value of funds to be added.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            session = get_session()
            cursor = session.query(User).filter(User.id == user_id)
            result = cursor.first()

            if result is None:
                session.close()
                return error.error_non_exist_user_id(user_id)

            if result.password != password:
                session.close()
                return error.error_authorization_fail()

            # balance += add_value
            cursor.update({"balance": User.balance + add_value})

            session.commit()
            session.close()
        except SQLAlchemyError as e:
            logging.error(e)
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(e)
            session.rollback()
            return 530, "{}".format(str(e))
        return 200, "ok"

    @staticmethod
    def mark_order_received(
        user_id: str, password: str, order_id: str
    ) -> Tuple[int, str]:
        """Mark an order as received by user.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        password : str
            The password of the buyer.

        order_id : str
            The order_id of the received order.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            # Part 1. Check the user password.
            session = get_session()
            result = session.query(User).filter(User.id == user_id).first()

            if result is None:
                session.close()
                return error.error_non_exist_user_id(user_id)

            if result.password != password:
                session.close()
                return error.error_authorization_fail()

            # Part 2. Update the order status
            cursor = session.query(Order).filter(Order.id == order_id)
            result = cursor.first()

            if result is None:
                session.close()
                return error.error_non_exist_order_id(order_id)

            if result.status != "delivered":
                session.close()
                return error.error_order_status(result.status)

            if result.buyer != user_id:
                session.close()
                return error.error_user_id_match(result.buyer, user_id)

            # Part 3. Get the store.
            store_result = (
                session.query(Store).filter(Store.id == result.store_id).first()
            )
            if store_result is None:
                session.close()
                return error.error_non_exist_store_id(result.store_id)

            seller = store_result.owner

            # seller's balance += total_price
            session.query(User).filter(User.id == seller).update(
                {"balance": User.balance + result.total_price}
            )

            # update the order status
            session.query(Order).filter(Order.id == order_id).update(
                {"status": "finished"}
            )
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            logging.error(e)
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(e)
            session.rollback()
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def cancel_order(user_id: str, password: str, order_id: str) -> Tuple[int, str]:
        """The buyer cancels an order.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        password : str
            The password of the buyer.

        order_id : str
            The order_id of the canceled order.

        Returns
        -------
        (code : int, msg : str)
            The return status.
        """
        try:
            session = get_session()
            result = session.query(User).filter(User.id == user_id).first()
            if result is None:
                session.close()
                return error.error_non_exist_user_id(user_id)

            if result.password != password:
                session.close()
                return error.error_authorization_fail()

            result = session.query(Order).filter(Order.id == order_id).first()
            if result is None:
                return error.error_non_exist_order_id(order_id)

            order_status = result.status
            store = result.store_id
            total_price = result.total_price

            if order_status == "canceled" or order_status == "finished":
                return error.error_order_status(order_status)

            # for the book stock
            book_orders = (
                session.query(OrderDetail)
                .filter(OrderDetail.order_id == order_id)
                .all()
            )
            for book_order in book_orders:
                session.query(Book).filter_by(
                    id=book_order.book_id, store_id=store
                ).update(
                    {
                        "stock_level": Book.stock_level + book_order.count,
                    },
                )

            # for back money
            if order_status == "paid" or order_status == "delivered":
                # buyer's balance -= total_price
                session.query(User).filter(User.id == user_id).update(
                    {"balance": User.balance + total_price},
                )
            # update the order status
            session.query(Order).filter(Order.id == order_id).update(
                {"status": "canceled"}
            )
            session.commit()
            session.close()
        except SQLAlchemyError as e:
            logging.error(e)
            session.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.error(e)
            session.rollback()
            return 530, "{}".format(str(e))

        return 200, "ok"

    @staticmethod
    def query_all_orders(user_id: str, password: str) -> Tuple[int, str, list]:
        """A buyer queries all his orders.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        password : str
            The password of the buyer.

        Returns
        -------
        (code : int, msg : str, orders: List[dict])
            The return status and the queried orders.
        """
        try:
            session = get_session()
            result = session.query(User).filter(User.id == user_id).first()
            if result is None:
                session.close()
                return error.error_non_exist_user_id(user_id) + ([],)

            if result.password != password:
                session.close()
                return error.error_authorization_fail() + ([],)

            orders = session.query(Order).filter(Order.buyer == user_id).all()
        except SQLAlchemyError as e:
            session.close()
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            session.close()
            return 530, "{}".format(str(e)), []

        result = [to_dict(order) for order in orders]
        return 200, "ok", result

    @staticmethod
    def query_one_order(
        user_id: str, password: str, order_id: str
    ) -> Tuple[int, str, dict]:
        """A buyer queries one specified order.

        Parameters
        ----------
        user_id : str
            The user_id of the buyer.

        password : str
            The password of the buyer.

        order_id : str
            the order_id of the queried order.

        Returns
        -------
        (code : int, msg : str, order : dict)
            The return status and the queried order.
        """
        try:
            session = get_session()
            result = session.query(User).filter(User.id == user_id).first()
            if result is None:
                session.close()
                return error.error_non_exist_user_id(user_id) + ({},)

            if result.password != password:
                session.close()
                return error.error_authorization_fail() + ({},)

            order = session.query(Order).filter(Order.id == order_id).first()
            if order is None:
                session.close()
                return error.error_non_exist_order_id(order_id) + ({},)
            session.close()
        except SQLAlchemyError as e:
            logging.error(e)
            session.close()
            return 528, "{}".format(str(e)), {}
        except BaseException as e:
            logging.error(e)
            session.close()
            return 530, "{}".format(str(e)), {}
        return 200, "ok", to_dict(order)
