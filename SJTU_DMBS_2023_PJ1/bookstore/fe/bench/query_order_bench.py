from fe.bench.workload import Workload
from fe.bench.workload import QueryOneOrder
from fe.bench.workload import QueryAllOrders
import time
import random


class QueryOrderBench:
    def __init__(self, wl: Workload):
        self.workload = wl
        self.new_order_request = []
        self.time_query_order = 0
        self.gen_procedure()

    def gen_procedure(self):
        for i in range(0, self.workload.procedure_per_session):
            new_order = self.workload.get_new_order()
            self.new_order_request.append(new_order)

    def run_order_query_bench(self, query_num: int):
        order_ids = []

        for new_order in self.new_order_request:
            ok, order_id = new_order.run()
            assert ok
            order_ids.append(order_id)

        for _ in range(query_num):
            order_ind = random.randint(1, len(self.new_order_request))
            buyer, order_id = (
                self.new_order_request[order_ind - 1].buyer,
                order_ids[order_ind - 1],
            )
            # one order
            query = QueryOneOrder(buyer, order_id)
            before = time.time()
            ok = query.run()
            after = time.time()
            self.time_query_order = self.time_query_order + after - before
            assert ok

            # all orders
            query = QueryAllOrders(buyer, order_id)
            before = time.time()
            ok = query.run()
            after = time.time()
            self.time_query_order = self.time_query_order + after - before
            assert ok
