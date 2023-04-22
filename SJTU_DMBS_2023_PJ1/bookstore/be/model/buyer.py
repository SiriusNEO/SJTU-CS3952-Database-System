"""Buyer related APIs."""

import time
import uuid
import json
import pymongo
import logging
from be.model import error
from be.model.mongo_manager import (
    get_user_col,
    get_store_col,
    get_order_col,
    get_book_col,
    user_id_exists,
    store_id_exists,
    order_id_exists,
    book_id_exists,
)
from be.model.utils import check_expired


class BuyerAPI:
    """Backend APIs related to buyer manipulation."""

    @staticmethod
    def new_order(
        user_id: str,
        store_id: str,
        books: [(str, int)],
    ) -> (int, str, str):
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
        order_id = ""
        try:
            if not user_id_exists(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not store_id_exists(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)

            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            total_price = 0
            order_data_books = []

            for book_id, count in books:
                cursor = get_book_col().find_one(
                    {
                        "_id": {
                            "store_id": store_id,
                            "book_id": book_id,
                        }
                    },
                )
                if cursor is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = cursor["stock_level"]
                price = cursor["price"]

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor = get_book_col().update_one(
                    {
                        "_id": {
                            "store_id": store_id,
                            "book_id": book_id,
                        }
                    },
                    {"$inc": {"stock_level": -count}},
                )
                assert cursor.matched_count > 0
                assert cursor.modified_count == cursor.matched_count

                total_price += count * price
                order_data_books.append(
                    {"book_id": book_id, "count": count, "price": price}
                )

            order_id = uid
            now_time = time.time()
            get_order_col().insert_one(
                {
                    "_id": order_id,
                    "buyer": user_id,
                    "store": store_id,
                    "total_price": total_price,
                    "books": order_data_books,
                    "state": "unpaid",
                    "timestamp": now_time,
                }
            )
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, "ok", order_id

    @staticmethod
    def payment(user_id: str, password: str, order_id: str) -> (int, str):
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
            cursor = get_order_col().find_one({"_id": order_id})
            if cursor is None:
                return error.error_non_exist_order_id(order_id)
            if cursor["state"] != "unpaid":
                return error.error_order_state(cursor["state"])
            if cursor["buyer"] != user_id:
                return error.error_authorization_fail()

            if check_expired(cursor["timestamp"]):
                code, message = self.cancel_order(user_id, password, order_id)
                if code != 200:
                    return code, message

            total_price = cursor["total_price"]

            cursor = get_user_col().find_one({"_id": user_id})
            if cursor is None:
                return error.error_non_exist_user_id(user_id)
            if password != cursor["password"]:
                return error.error_authorization_fail()

            balance = cursor["balance"]

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # buyer's balance -= total_price
            get_user_col().update_one(
                {"_id": user_id}, {"$inc": {"balance": -total_price}}
            )

            # cursor = get_store_col().find_one({"_id": store})
            # if cursor is None:
            #     return error.error_non_exist_store_id(store)
            # seller = cursor["owner"]
            # # seller's balance += total_price
            # get_user_col().update_one(
            #     {"_id": seller}, {"$inc": {"balance": total_price}}
            # )

            # # delete the order
            # result = get_order_col().delete_one({"_id": order_id})
            # assert result.deleted_count == 1

            # update the order state
            get_order_col().update_one({"_id": order_id}, {"$set": {"state": "paid"}})
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    @staticmethod
    def add_funds(user_id: str, password: str, add_value: int) -> (int, str):
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
            cursor = get_user_col().find_one({"_id": user_id})
            if cursor is None:
                return error.error_non_exist_user_id(user_id)

            if cursor["password"] != password:
                return error.error_authorization_fail()

            # balance += add_value
            get_user_col().update_one(
                {"_id": user_id}, {"$inc": {"balance": add_value}}
            )
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    @staticmethod
    def mark_order_received(user_id: str, password: str, order_id: str) -> (int, str):
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
            cursor = get_user_col().find_one({"_id": user_id})
            if cursor is None:
                return error.error_non_exist_user_id(user_id)

            if cursor["password"] != password:
                return error.error_authorization_fail()

            cursor = get_order_col().find_one({"_id": order_id})
            if cursor is None:
                return error.error_non_exist_order_id(order_id)

            if cursor["state"] != "delivered":
                return error.error_order_state(cursor["state"])

            if cursor["buyer"] != user_id:
                return error.error_user_id_match(cursor["buyer"], user_id)

            store_cursor = get_store_col().find_one({"_id": cursor["store"]})
            if store_cursor is None:
                return error.error_non_exist_store_id(cursor["store"])

            seller = store_cursor["owner"]
            # seller's balance += total_price
            get_user_col().update_one(
                {"_id": seller}, {"$inc": {"balance": cursor["total_price"]}}
            )

            # update the order state
            get_order_col().update_one(
                {"_id": order_id}, {"$set": {"state": "finished"}}
            )
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    @staticmethod
    def cancel_order(user_id: str, password: str, order_id: str) -> (int, str):
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
            cursor = get_user_col().find_one({"_id": user_id})
            if cursor is None:
                return error.error_non_exist_user_id(user_id)

            if cursor["password"] != password:
                return error.error_authorization_fail()

            if not order_id_exists(order_id):
                return error.error_non_exist_order_id(order_id)

            cursor = get_order_col().find_one({"_id": order_id})
            if cursor["state"] == "canceled" or cursor["state"] == "finished":
                return error.error_order_state(cursor["state"])

            # for the book stock
            for book in cursor["books"]:
                book_cursor = get_book_col().find_one(
                    {
                        "_id": {
                            "store_id": cursor["store"],
                            "book_id": book["book_id"],
                        }
                    },
                )

                # in the list of the order, so it must exist
                assert book_cursor is not None

                book_cursor = get_book_col().update_one(
                    {
                        "_id": {
                            "store_id": cursor["store"],
                            "book_id": book["book_id"],
                        }
                    },
                    {"$inc": {"stock_level": book["count"]}},
                )

            # for back money
            if cursor["state"] == "paid" or cursor["state"] == "delivered":
                # buyer's balance -= total_price
                get_user_col().update_one(
                    {"_id": user_id}, {"$inc": {"balance": cursor["total_price"]}}
                )
            # update the order state
            get_order_col().update_one(
                {"_id": order_id}, {"$set": {"state": "canceled"}}
            )

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    @staticmethod
    def query_all_orders(user_id: str, password: str) -> (int, str, list):
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
            cursor = get_user_col().find_one({"_id": user_id})
            if cursor is None:
                return error.error_non_exist_user_id(user_id) + ([],)

            if cursor["password"] != password:
                return error.error_authorization_fail() + ([],)

            order_cursors = get_order_col().find({"buyer": user_id})

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", list(order_cursors)

    @staticmethod
    def query_one_order(user_id: str, password: str, order_id: str) -> (int, str, dict):
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
            cursor = get_user_col().find_one({"_id": user_id})
            if cursor is None:
                return error.error_non_exist_user_id(user_id) + ({},)

            if cursor["password"] != password:
                return error.error_authorization_fail() + ({},)

            cursor = get_order_col().find_one({"_id": order_id})
            if cursor is None:
                return error.error_non_exist_order_id(order_id) + ({},)

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), {}
        except BaseException as e:
            return 530, "{}".format(str(e)), {}
        return 200, "ok", cursor
