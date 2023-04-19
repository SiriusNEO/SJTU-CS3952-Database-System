import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid
import time


class TestOrderState:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_order_state_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_order_state_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_order_state_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, low_stock_level=False, max_book_count=5
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num
        yield

    def test_one_order_ok(self):
        code, order = self.buyer.query_one_order(self.order_id)
        assert code == 200

        assert order["_id"] == self.order_id
        for i, (book, count) in enumerate(self.buy_book_info_list):
            assert order["books"][i]["book_id"] == book.id
            assert order["books"][i]["price"] == book.price
            assert order["books"][i]["count"] == count

    def test_all_orders_ok(self):
        code, self.order_id1 = self.buyer.new_order(self.store_id, [])
        assert code == 200

        code, orders = self.buyer.query_all_orders()
        assert code == 200

        assert len(orders) == 2

        order = orders[0]

        assert order["_id"] == self.order_id
        for i, (book, count) in enumerate(self.buy_book_info_list):
            assert order["books"][i]["book_id"] == book.id
            assert order["books"][i]["price"] == book.price
            assert order["books"][i]["count"] == count

    def test_one_order_authorization_error(self):
        self.buyer.password += "_x"
        code, order = self.buyer.query_one_order(self.order_id)
        assert code == 401

    def test_all_orders_authorization_error(self):
        self.buyer.password += "_x"
        code, order = self.buyer.query_all_orders()
        assert code == 401

    def test_one_order_non_exist_order(self):
        code, order = self.buyer.query_one_order("xxx")
        assert code == 520

    def test_one_order_non_exist_user(self):
        self.buyer.user_id = "xxx"
        code, order = self.buyer.query_one_order(self.order_id)
        assert code == 511

    def test_all_orders_non_exist_user(self):
        self.buyer.user_id = "xxx"
        code, order = self.buyer.query_all_orders()
        assert code == 511
