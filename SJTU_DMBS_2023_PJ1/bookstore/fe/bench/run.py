from fe.bench.workload import Workload
from fe.bench.session import Session
from fe.bench.query_order_bench import QueryOrderBench
from fe.bench.query_book_bench import QueryBookBench
from fe import conf


def run_bench(show_stat=False):
    wl = Workload()
    wl.gen_database()

    sessions = []
    for i in range(0, wl.session):
        ss = Session(wl)
        sessions.append(ss)

    for ss in sessions:
        ss.start()

    for ss in sessions:
        ss.join()

    time_new_order = 0
    time_payment = 0
    for ss in sessions:
        time_new_order += ss.time_new_order
        time_payment += ss.time_payment

    if show_stat:
        print(
            f"Bench Result: time_new_order={time_new_order:.4}, time_payment={time_payment:.4}"
        )


def run_query_order_bench(show_stat=False):
    wl = Workload()
    wl.gen_database()

    bench = QueryOrderBench(wl)
    bench.run_order_query_bench(conf.Bench_Order_Queries_Num)

    if show_stat:
        print(f"Bench Result: time_query_order={bench.time_query_order:.4}")


def run_query_book_bench(show_stat=False):
    wl = Workload()
    wl.gen_database()

    bench = QueryBookBench(wl)
    bench.run_order_book_bench(conf.Bench_Book_Queries_Num)

    if show_stat:
        print(f"Bench Result: time_query_book={bench.time_query_book:.4}")


# if __name__ == "__main__":
# run_bench(show_stat=True)
# run_query_order_bench(show_stat=True)
# run_query_book_bench(show_stat=True)
