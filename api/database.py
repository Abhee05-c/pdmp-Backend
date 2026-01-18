from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_url="postgresql://postgres:notforget%4002!@localhost:5432/pdmpApp"

engine=create_engine(database_url)

Session_local=sessionmaker(bind=engine, autoflush=False, expire_on_commit=False
)

