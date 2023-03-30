import pymongo


client = pymongo.MongoClient("mongodb://localhost:27017/")

print("Connect finish: ", client)

db = client["bookstore"]
print(client.list_database_names())

store = db["store"]
print(store)

store_data1 = {
    "_id": "store_1",
    "owner": "lcf",
    "book_list": [
        {"book_id": "book1", "stock_level": 233},
        {"book_id": "book2", "stock_level": 666},
    ]
}

store.delete_many({})
store.insert_one(store_data1)

try:
    store.insert_one(store_data1)
except pymongo.errors.DuplicateKeyError as e:
    print("123")
except pymongo.errors.PyMongoError as e:
    print("{}".format(str(e)))

# content = store.find()
# for each in content:
#     print(each)

# content = store.find({}, {"_id": 0, "book_list": {"$elemMatch": {"book_id": "book1"}}})
# content = store.find({}, {"owner": 1})
# for each in content:
#     print(each)
