"""Seller related APIs."""

import pymongo
import logging
from be.model import error
from be.model.mongo_manager import (
    get_store_col,
    get_book_col,
    get_user_col,
    get_order_col,
    user_id_exists,
    store_id_exists,
    book_id_exists,
    order_id_exists,
)


class SellerAPI:
    """Backend APIs related to seller manipulation."""

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_info: dict,
        stock_level: int,
    ) -> (int, str):
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

            book_info.update(
                {
                    "_id": {
                        "store_id": store_id,
                        "book_id": book_id,
                    },
                    "stock_level": stock_level,
                }
            )
            get_book_col().insert_one(book_info)
        except pymongo.errors.DuplicateKeyError as e:
            return error.error_exist_book_id(book_id)
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ) -> (int, str):
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

            cursor = get_book_col().update_one(
                {
                    "_id": {
                        "store_id": store_id,
                        "book_id": book_id,
                    },
                },
                {
                    "$inc": {
                        "stock_level": add_stock_level,
                    }
                },
            )

            if cursor.matched_count == 0:
                return error.error_non_exist_book_id(book_id)
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
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

            get_store_col().insert_one(
                {
                    "_id": store_id,
                    "owner": user_id,
                }
            )
        except pymongo.errors.DuplicateKeyError as e:
            return error.error_exist_store_id(store_id)
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"

    def mark_order_shipped(self, store_id: str, order_id: str) -> (int, str):
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
            if not order_id_exists(order_id):
                return error.error_non_exist_order_id(order_id)
            if not store_id_exists(store_id):
                return error.error_non_exist_store_id(store_id)

            cursor = get_order_col().find_one({"_id": order_id})
            if cursor is None:
                return error.error_invalid_order_id(order_id)

            if cursor["state"] != "paid":
                return error.error_order_state_id(cursor["state"])

            if cursor["store"] != store_id:
                return error.error_store_id_match(cursor["store"], store_id)

            # update the order state
            get_order_col().update_one(
                {"_id": order_id}, {"$set": {"state": "delivered"}}
            )

        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"
