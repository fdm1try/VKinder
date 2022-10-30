import sqlalchemy as sq
from sqlalchemy import create_engine, Column, Integer, ForeignKey, CheckConstraint
import psycopg2
from config import DB_LOGIN, DB_PASS
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DSN_ORM = 'postgresql+psycopg2://{0}:{1}@localhost:5432/bot'.format(DB_LOGIN, DB_PASS)
engine_orm = create_engine(DSN_ORM)
Session_orm = sessionmaker(bind=engine_orm)
Base = declarative_base()

with psycopg2.connect(user=DB_LOGIN, password =DB_PASS) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT 'CREATE DATABASE bot'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bot')""")

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, nullable=False)
    sex = Column(Integer, nullable=False)
    stage = Column(Integer)
    age_from = Column(Integer, nullable=False)
    age_to = Column(Integer, nullable=False)
    search_status = Column(Integer, nullable=False)
    offset = Column(Integer, nullable=False)
    __table_args__ = (CheckConstraint(stage >= 0), CheckConstraint(sex.in_([1,2])), CheckConstraint(search_status.in_([1,6])))

class Favourites(Base):
    __tablename__ = 'favourites'

    vk_user_id = Column(Integer, primary_key=True)
    user_id = Column(sq.Integer, ForeignKey('users.id'), unique=True)
    users = relationship('Users', backref = 'favourites')
    
class Blacklist(Base):
    __tablename__ = 'blacklist'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(sq.Integer, ForeignKey('users.id'), unique=True)
    vk_user_id = Column(Integer, unique=True, nullable=False)
    users = relationship('Users', backref = 'blacklist')
    
   
class User_search_history(Base):
    __tablename__ = 'user_search_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(sq.Integer, ForeignKey('users.id'), unique=True)
    vk_user_id = Column(Integer, unique=True, nullable=False)
    users = relationship('Users', backref = 'search_history')
    
def create_tables(engine_orm):
    Base.metadata.drop_all(engine_orm)
    Base.metadata.create_all(engine_orm)
    
with Session_orm():
    create_tables(engine_orm)