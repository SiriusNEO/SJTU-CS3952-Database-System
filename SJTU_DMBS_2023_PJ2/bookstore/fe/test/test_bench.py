from fe.bench.run import run_bench, run_query_order_bench, run_query_book_bench


def test_bench():
    try:
        run_bench()
    except Exception as e:
        assert 200 == 100, "test_bench 过程出现异常"


def test_query_order_bench():
    try:
        run_query_order_bench()
    except Exception as e:
        assert 200 == 100, "test_query_order_bench 过程出现异常"


def test_query_books_bench():
    try:
        run_query_book_bench()
    except Exception as e:
        assert 200 == 100, "test_query_books_bench 过程出现异常"
