from typing import Union
import logging
import os
import pymongo


class MongoManager:
    """The all-in-one manager for the MongoDB database in this bookstore application."""

    USER_COL_NAME: str = "user"
    BOOK_COL_NAME: str = "book"
    STORE_COL_NAME: str = "store"
    ORDER_COL_NAME: str = "order"

    def __init__(
        self,
        host: str = "localhost",
        port: Union[str, int] = 27017,
        db_name: str = "bookstore",
    ):
        # init connection
        self.client = pymongo.MongoClient(f"mongodb://{host}:{port}/")
        self.db_name = db_name
        self.database = self.client[db_name]

        # create collections
        self.user_col = self.database[self.USER_COL_NAME]
        self.book_col = self.database[self.BOOK_COL_NAME]
        self.store_col = self.database[self.STORE_COL_NAME]
        self.order_col = self.database[self.ORDER_COL_NAME]

        # create index for orders
        self.order_col.create_index([("user_id", 1)])

        # create index for books
        self.book_col.create_index([("id", 1)])

        # create text index for title
        self.book_col.create_index([("title", pymongo.TEXT)])

        self.book_col.create_index([("author", 1)])
        self.book_col.create_index([("publisher", 1)])
        self.book_col.create_index([("original_title", 1)])
        self.book_col.create_index([("translator", 1)])
        self.book_col.create_index([("pub_year", 1)])
        self.book_col.create_index([("pages", 1)])
        self.book_col.create_index([("price", 1)])
        self.book_col.create_index([("currency_unit", 1)])
        self.book_col.create_index([("binding", 1)])
        self.book_col.create_index([("isbn", 1)])

        # This columns are too big to make index or make hashed index for substitution
        # self.book_col.create_index([("author_intro",1)])
        # self.book_col.create_index([("book_intro",1)])
        # self.book_col.create_index([("content",1)])

        # init finish. display current index
        logging.info("MongoDB manager init finish.")
        logging.info(
            "Collection User Indices: "
            + str(list(dict(self.user_col.index_information()).keys()))
        )
        logging.info(
            "Collection Book Indices: "
            + str(list(dict(self.book_col.index_information()).keys()))
        )
        logging.info(
            "Collection Store Indices: "
            + str(list(dict(self.store_col.index_information()).keys()))
        )
        logging.info(
            "Collection Order Indices: "
            + str(list(dict(self.order_col.index_information()).keys()))
        )


# Global instance of the manager
glb_manager: MongoManager = None

# Lazy initialization
def init_database(
    host: str = "localhost",
    port: Union[str, int] = 27017,
    db_name: str = "bookstore",
):
    global glb_manager
    glb_manager = MongoManager(host, port, db_name)


# APIs to get the collections from the global instance.
def get_user_col():
    global glb_manager
    return glb_manager.user_col


def get_book_col():
    global glb_manager
    return glb_manager.book_col


def get_store_col():
    global glb_manager
    return glb_manager.store_col


def get_order_col():
    global glb_manager
    return glb_manager.order_col


# APIs to check id existence.
def user_id_exists(user_id: str) -> bool:
    return get_user_col().count_documents({"_id": user_id}) > 0


def store_id_exists(store_id: str) -> bool:
    return get_store_col().count_documents({"_id": store_id}) > 0


def order_id_exists(order_id: str) -> bool:
    return get_order_col().count_documents({"_id": order_id}) > 0


def book_id_exists(book_id: str) -> bool:
    return get_book_col().count_documents({"_id": book_id}) > 0
