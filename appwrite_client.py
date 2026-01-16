from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage

client = Client()
client.set_endpoint("https://cloud.appwrite.io/v1")
client.set_project("6969c95900290570ce1e")
client.set_key("standard_7552a470bdd52a171b97f0a7daa3eb44ac0730d11e95f63592cc58e9c75e85cac746fff7e0ae5c72e5fcc1edc05156105ef711737b64592c04ac7ef972d939e91b671f37f2e1c558d46a64faf6c646990fa02e76b9c3c57013b9826783d1768640d05d3ba4df903af5c82267ae0b4f0d9583e6f2fb317bd8f3376b8e6c517d59")

database = Databases(client)
storage = Storage(client)

DATABASE_ID = "6969ca21000b0d7450ce"
COLLECTION_ID = "submission"
BUCKET_ID = "6969cb540031c7c906bd"
