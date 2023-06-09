import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access.book import Book
import uuid
import time


class TestShipAndReceiveOrder:
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
        self.seller_id = "test_ship_and_receive_order_seller_id_{}".format(
            str(uuid.uuid1())
        )
        self.store_id = "test_ship_and_receive_order_store_id_{}".format(
            str(uuid.uuid1())
        )
        self.buyer_id = "test_ship_and_receive_order_buyer_id_{}".format(
            str(uuid.uuid1())
        )
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
        self.seller = gen_book.seller
        yield

    def test_one_round_ship_and_receive_ok(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200

        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = self.seller.mark_order_shipped(self.store_id, self.order_id)
        assert code == 200

        code = self.buyer.mark_order_received(self.order_id)
        assert code == 200

    def test_ship_non_exist_order_id(self):
        code = self.seller.mark_order_shipped(self.store_id, "xxx")
        assert code == 520

    def test_ship_unpaid(self):
        code = self.seller.mark_order_shipped(self.store_id, self.order_id)
        assert code == 522

    def test_ship_non_exist_store_id(self):
        code = self.seller.mark_order_shipped("xxx", self.order_id)
        assert code == 513

    def test_ship_store_id_unmatch(self):
        store_id1 = "test_ship_and_receive_order_store_id_{}".format(str(uuid.uuid1()))
        self.seller.create_store(store_id1)

        code = self.buyer.add_funds(self.total_price)
        assert code == 200

        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = self.seller.mark_order_shipped(store_id1, self.order_id)
        assert code == 524

    def test_receive_without_shipping(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200

        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = self.buyer.mark_order_received(self.order_id)
        assert code != 200

    def test_receive_invalid_user(self):
        self.buyer.user_id = "xxx"
        code = self.buyer.mark_order_received(self.order_id)
        assert code == 511

    def test_receive_wrong_passwd(self):
        self.buyer.password += "_x"
        code = self.buyer.mark_order_received(self.order_id)
        assert code == 401

    def test_receive_non_exist_order_id(self):
        code = self.buyer.mark_order_received("xxx")
        assert code == 520

    def test_receive_by_another_guy(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200

        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = self.seller.mark_order_shipped(self.store_id, self.order_id)
        assert code == 200

        b1 = register_new_buyer(
            "test_ship_and_receive_order_buyer_id_{}".format(str(uuid.uuid1())),
            self.password,
        )

        code = b1.mark_order_received(self.order_id)
        assert code == 523
