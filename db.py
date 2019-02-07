from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


database_url = 'postgres://dceraqvcqhmcgu:19271607429d1f3ca9e649f3ea13a61bee4794f7f11ffb622c52a8a74cf87b22@ec2-54-235-68-3.compute-1.amazonaws.com:5432/d4vk8nvjg5nipp'

engine = create_engine(database_url, convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
    autoflush=False,
    bind=engine))
Base = declarative_base()

Base.query = db_session.query_property()

