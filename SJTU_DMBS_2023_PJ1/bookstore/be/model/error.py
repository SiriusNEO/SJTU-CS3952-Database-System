error_code = {
    401: "authorization fail.",
    511: "non exist user id {}",
    512: "exist user id {}",
    513: "non exist store id {}",
    514: "exist store id {}",
    515: "non exist book id {}",
    516: "exist book id {}",
    517: "stock level low, book id {}",
    518: "",
    519: "not sufficient funds, order id {}",
    520: "non exist order id",
    521: "exist order id",
    522: "the order state is error, order state: {}",
    523: "the user is not match {},{}",
    524: "the store is not match {},{}",
    525: "invalid behaviour in query book API",
    526: "",
    527: "",
    528: "",
}


def error_non_exist_user_id(user_id):
    return 511, error_code[511].format(user_id)


def error_exist_user_id(user_id):
    return 512, error_code[512].format(user_id)


def error_non_exist_store_id(store_id):
    return 513, error_code[513].format(store_id)


def error_exist_store_id(store_id):
    return 514, error_code[514].format(store_id)


def error_non_exist_book_id(book_id):
    return 515, error_code[515].format(book_id)


def error_exist_book_id(book_id):
    return 516, error_code[516].format(book_id)


def error_stock_level_low(book_id):
    return 517, error_code[517].format(book_id)


# def error_non_exist_order_id(order_id):
#     return 518, error_code[518].format(order_id)


def error_not_sufficient_funds(order_id):
    return 519, error_code[518].format(order_id)


def error_non_exist_order_id(order_id):
    return 520, error_code[515].format(order_id)


def error_exist_order_id(order_id):
    return 521, error_code[521].format(order_id)


def error_order_state(order_state):
    return 522, error_code[522].format(order_state)


def error_user_id_match(user1, user2):
    return 523, error_code[523].format(user1, user2)


def error_store_id_match(store1, store2):
    return 524, error_code[524].format(store1, store2)


def error_invalid_query_book_behaviour():
    return 525, error_code[525].format()


def error_authorization_fail():
    return 401, error_code[401]


def error_and_message(code, message):
    return code, message
