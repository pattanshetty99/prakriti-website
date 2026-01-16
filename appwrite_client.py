from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage

client = Client()
client.set_endpoint("APPWRITE_ENDPOINT")
client.set_project("APPWRITE_PROJECT_ID")
client.set_key("APPWRITE_API_KEY")

database = Databases(client)
storage = Storage(client)

DATABASE_ID = "DATABASE_ID"
COLLECTION_ID = "COLLECTION_ID"
BUCKET_ID = "BUCKET_ID"
