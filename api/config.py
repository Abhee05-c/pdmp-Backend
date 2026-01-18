from dotenv import load_dotenv
import os

load_dotenv()

Secret_key = os.getenv("Secret_key")
database_url = os.getenv("database_url")

if not Secret_key:
    raise RuntimeError("Secret_key is missing")

if not database_url:
    raise RuntimeError("database_url missing")
