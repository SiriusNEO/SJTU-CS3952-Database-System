"""Search related APIs."""

from typing import Tuple

import logging

from be.model.base import get_session, Book
from sqlalchemy.exc import SQLAlchemyError
from be.model.error import error_invalid_query_book_behaviour
from be.model.utils import to_dict, serialize_dict


class SearchAPI:
    @staticmethod
    def query_book(**kwargs) -> Tuple[int, str, list]:
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
                currency_unit
                title_keyword

        Returns
        -------
        (code : int, msg : str, books: list)
            The return status and the queried books.
        """
        try:
            session = get_session()
            cursor = session.query(Book)

            if "title_keyword" in kwargs:
                if "title" in kwargs:
                    return error_invalid_query_book_behaviour() + ([],)
                title_keyword = kwargs.pop("title_keyword")
                cursor = cursor.filter(Book.title.like(f"%{title_keyword}%"))

            if kwargs:
                kwargs = serialize_dict(kwargs)
                cursor = cursor.filter_by(**kwargs)

            books = cursor.all()
            session.close()
            ret = [to_dict(book) for book in books]
        except SQLAlchemyError as e:
            logging.error(e)
            session.close()
            return 528, "{}".format(str(e)), None
        except BaseException as e:
            logging.error(e)
            session.close()
            return 530, "{}".format(str(e)), None
        return 200, "ok", ret
