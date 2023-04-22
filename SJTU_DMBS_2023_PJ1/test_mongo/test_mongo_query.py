import pymongo


client = pymongo.MongoClient("mongodb://localhost:27017/")

print("Connect finish: ", client)

db = client["bookstore"]
print(client.list_database_names())

store = db["store"]
print(store)

store.create_index([("owner", pymongo.TEXT)])

info = store.index_information()
info = dict(info)
print(info)

store_data1 = {
    "_id": "store_1",
    "owner": "阿斯蒂芬",
    "owner1": "lcf",
    "book_list": [
        {"book_id": "book1", "stock_level": 233},
        {"book_id": "book2", "stock_level": 666},
    ],
}

store.delete_many({})
store.insert_one(store_data1)

# try:
#     store.insert_one(store_data1)
# except pymongo.errors.DuplicateKeyError as e:
#     print("123")
# except pymongo.errors.PyMongoError as e:
#     print("{}".format(str(e)))

print("bomb")

content = store.find({"owner": {"$regex": "阿斯"}})
print(list(content))

# content = store.find()
# for each in content:
#     print(each)

# content = store.find({}, {"_id": 0, "book_list": {"$elemMatch": {"book_id": "book1"}}})
# content = store.find({}, {"owner": 1})
# for each in content:
#     print(each)
