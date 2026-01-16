import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage

client = Client()

client.set_endpoint(os.environ.get("APPWRITE_ENDPOINT"))
client.set_project(os.environ.get("APPWRITE_PROJECT_ID"))
client.set_key(os.environ.get("APPWRITE_API_KEY"))

database = Databases(client)
storage = Storage(client)

DATABASE_ID = os.environ.get("DATABASE_ID")
COLLECTION_ID = os.environ.get("COLLECTION_ID")
BUCKET_ID = os.environ.get("BUCKET_ID")
