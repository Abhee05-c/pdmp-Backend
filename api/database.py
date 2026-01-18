from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.config import database_url


engine=create_engine(database_url)

Session_local=sessionmaker(bind=engine, autoflush=False, expire_on_commit=False
)

