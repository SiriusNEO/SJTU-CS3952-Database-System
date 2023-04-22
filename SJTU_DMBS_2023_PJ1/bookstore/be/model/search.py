"""Search related APIs."""

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
from be.model.error import error_invalid_query_book_behaviour


class SearchAPI:
    @staticmethod
    def query_book(**kwargs) -> (int, str, list):
        """
        Query books

        Parameters
        ----------
        kwargs : dict
            The restriction of this query.

            The keys of this dict can be:
                id
                store_id
                title
                author
                publisher
                original_title
                translator
                pub_year
                pages
                price
                currency_unit
                binding
                isbn
                author_intro
                book_intro
                content
                title_keyword

        Returns
        -------
        (code : int, msg : str, books: list)
            The return status and the queried books.
        """
        try:
            if "_id" in kwargs:
                return error_invalid_query_book_behaviour() + ([],)

            if "store_id" in kwargs:
                kwargs["_id.store_id"] = kwargs["store_id"]
                del kwargs["store_id"]

            if "title_keyword" in kwargs:
                if "title" in kwargs:
                    return error_invalid_query_book_behaviour() + ([],)

                kwd = kwargs["title_keyword"]
                del kwargs["title_keyword"]
                # kwargs["$text"] = {"$search": kwd}
                kwargs["title"] = {"$regex": kwd}

            cursor = get_book_col().find(kwargs)
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), None
        except BaseException as e:
            return 530, "{}".format(str(e)), None
        return 200, "ok", list(cursor)
