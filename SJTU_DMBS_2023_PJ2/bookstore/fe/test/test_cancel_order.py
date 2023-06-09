import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid
import time


class TestCancelOrder:
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
        self.seller_id1 = "test_cancel_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id1 = "test_cancel_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_cancel_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password1 = self.seller_id1
        gen_book1 = GenBook(self.seller_id1, self.store_id1)
        ok1, buy_book_id_list1 = gen_book1.gen(
            non_exist_book_id=False, low_stock_level=False, max_book_count=5
        )
        self.buy_book_info_list1 = gen_book1.buy_book_info_list
        assert ok1
        b = register_new_buyer(self.buyer_id, self.password1)
        self.buyer = b
        code, self.order_id1 = b.new_order(self.store_id1, buy_book_id_list1)
        assert code == 200
        self.total_price1 = 0
        for item in self.buy_book_info_list1:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price1 = self.total_price1 + book.price * num

        self.seller_id2 = "test_cancel_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id2 = "test_cancel_order_store_id_{}".format(str(uuid.uuid1()))
        self.password2 = self.seller_id2
        gen_book2 = GenBook(self.seller_id2, self.store_id2)
        ok2, buy_book_id_list2 = gen_book2.gen(
            non_exist_book_id=False, low_stock_level=False, max_book_count=5
        )
        self.buy_book_info_list2 = gen_book2.buy_book_info_list
        assert ok2
        # b2 = register_new_buyer(self.buyer_id, self.password2)
        code, self.order_id2 = b.new_order(self.store_id2, buy_book_id_list2)
        assert code == 200
        self.total_price2 = 0
        for item in self.buy_book_info_list2:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price2 = self.total_price2 + book.price * num
        yield

    def test_ok(self):
        code = self.buyer.add_funds(self.total_price1)
        assert code == 200

        code = self.buyer.payment(self.order_id1)
        assert code == 200

        code = self.buyer.cancel_order(self.order_id1)
        assert code == 200

    def test_ok_two_orders(self):
        code = self.buyer.add_funds(self.total_price1 + self.total_price2 - 5)
        assert code == 200

        # order1 canceled
        code = self.buyer.payment(self.order_id1)
        assert code == 200
        code = self.buyer.cancel_order(self.order_id1)
        assert code == 200

        # so order2 has enough money
        code = self.buyer.payment(self.order_id2)
        assert code == 200
        code = self.buyer.cancel_order(self.order_id2)
        assert code == 200

    def test_non_exist_user(self):
        self.buyer.user_id = "xxx"
        code = self.buyer.cancel_order(self.order_id1)
        assert code == 511

    def test_authorization_error(self):
        self.buyer.password += "_x"
        code = self.buyer.cancel_order(self.order_id1)
        assert code == 401

    def test_non_exist_order(self):
        code = self.buyer.cancel_order("xxx")
        assert code == 520

    def test_repeat_cancel(self):
        code = self.buyer.add_funds(self.total_price1)
        assert code == 200

        code = self.buyer.payment(self.order_id1)
        assert code == 200

        code = self.buyer.cancel_order(self.order_id1)
        assert code == 200

        code = self.buyer.cancel_order(self.order_id1)
        assert code != 200
