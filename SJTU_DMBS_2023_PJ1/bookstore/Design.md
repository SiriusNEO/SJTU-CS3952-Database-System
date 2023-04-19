### sql 版本的表结构

##### Table User:

```
user_id: TEXT PRIMARY KEY
password: TEXT NOT NULL
balance: INTEGER NOT NULL
token: TEXT
terminal: TEXT
```



##### Table user_store:

```
user_id: TEXT
store_id: TEXT
PRIMARY KEY(user_id, store_id)
```



##### Table store:

```
store_id: TEXT
book_id: TEXT
book_info: TEXT
stock_level: INTEGER
PRIMARY KEY(store_id, book_id)
```



##### Table new_order:

```
order_id: TEXT PRIMARY KEY
user_id: TEXT
store_id: TEXT
```



##### Table new_order_detail:

```
order_id: TEXT
book_id: TEXT
count: INTEGER
price: INTEGER
PRIMARY KEY(order_id, book_id)
```



### Mongodb 版本表结构

##### Doc user

- _id (user_id)
- password
- balance
- token
- terminal
- own_stores (list, child reference)



##### Doc book

- _id (store_id, book_id)
- book_info (class, 比较复杂！以 json_str 形式？)
- stock_level



##### Doc store

- owner (user_id)
- _id (store_id)



##### Doc order

- order_id

- buyer (user_id)
- buy_from (store_id)
- total_price
- books (list)
  - book_id
  - count
  - price
- order_state (`Literal[unpaid, paid, delivered, canceled, finished]`)
