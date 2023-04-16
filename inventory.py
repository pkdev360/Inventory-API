from fastapi import FastAPI, Query
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import os
import urllib.parse
from pydantic import BaseModel
from typing import Optional


load_dotenv(find_dotenv())

get_user = os.environ.get('MONGODB_USR')
user = urllib.parse.quote(get_user)

get_password = os.environ.get('MONGODB_PWD')
password = urllib.parse.quote(get_password)

connection_str = f'mongodb+srv://{user}:{password}@dev360.mlhxacy.mongodb.net/?retryWrites=true&w=majority'

client = MongoClient(connection_str)

dbs = client.list_database_names()

print(dbs)

store = client.store

print(store.list_collection_names())


app = FastAPI()


class Inventory(BaseModel):
    book_name: str
    price: Optional[float] = None
    name: str


class UpdateInventory(BaseModel):
    price: Optional[float] = None
    name: Optional[str] = None


@app.get('/')
def home():
    return {'Data': 'Home'}


@app.get('/db-collections')
def db_collections():
    collections = store.list_collection_names()
    return collections


@app.post('/add-item/')
def add_item(inventory: Inventory):
    collection = store.inventory

    # Working
    # collection.insert_one({'testing': 'Amazing'})

    # Working with ".dict()"
    collection.insert_one(inventory.dict())
    return {"Data": f"Book: '{inventory.book_name}' successfully added into the database."}


@app.get('/book')
def book(book_name: str):
    collection = store.inventory
    book = collection.find_one({'book_name': book_name})
    if book:
        return {'Data Found': {'Book Name': f"{book['book_name']}", 'Author Name': f"{book['name']}", 'Price': f"{book['price']}"}}
    else:
        return {'Data': 'Book Not Found'}


@app.put('/update-book')
def update_book(book_name: str, item: UpdateInventory):
    collection = store.inventory
    book = collection.find_one({'book_name': book_name})

    update_book_info = {
        '$set': item.dict()
    }

    if not book:
        return {'Date': 'Book Doesn\'t exists.'}
    else:
        collection.update_one({'book_name': book_name}, update_book_info)
        updated_book = collection.find_one({'book_name': book_name})
        return {'Data Updated': {'Book Name': f"{updated_book['book_name']}", 'Author Name': f"{updated_book['name']}", 'Price': f"{updated_book['price']}"}}


@app.delete('/delete-item/')
def delete_item(item_id: str):
    from bson import ObjectId
    _id = ObjectId(item_id)

    collection = store.inventory

    id_found = collection.find_one({'_id': _id})

    if not id_found:
        return {"Data": f"Id not in Database."}
    else:
        collection.delete_one({'_id': _id})
        return {"Data": f"Item Id: \"{_id}\" deleted from the database."}
