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
from be.model.error import error_code

class SearchAPI:
    def query_book(self, **kwargs) -> (int, str, list):
        """
            Query books
            Parameters:
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
        """
        if '_id' in kwargs:
            return 525, error_code[525]
        
        if 'store_id' in kwargs:
            kwargs['_id.store_id'] = kwargs['store_id']
            del kwargs['store_id']

        cursor = get_book_col().find(kwargs)
        
        return 200, "ok", list(cursor)