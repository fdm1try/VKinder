from sqlalchemy import create_engine, Column, Integer, ForeignKey, CheckConstraint, String
from VKinder.config import DB_LOGIN, DB_PASS, DB_NAME
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DSN_ORM = "postgresql+psycopg2://{0}:{1}@localhost:5432/{2}".format(DB_LOGIN, DB_PASS, DB_NAME)
engine_orm = create_engine(DSN_ORM)
Session_orm = sessionmaker(bind=engine_orm)
Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    city_id = Column(Integer, nullable=False)
    sex = Column(Integer, nullable=False)
    stage = Column(Integer)
    age_from = Column(Integer, nullable=False)
    age_to = Column(Integer, nullable=False)
    search_status = Column(Integer, nullable=False)
    offset = Column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint(stage >= 0),
        CheckConstraint(sex.in_([1, 2])),
        CheckConstraint(search_status.in_([1, 6]))
    )

    favorites = relationship("Favorites")
    search_history = relationship("UserSearchHistory")
    blacklist = relationship("Blacklist")
    token = relationship("UserToken", back_populates="user", uselist=False)

    def __str__(self):
        return (
            f"Пользователь: Id: {self.id} город: {self.city_id} пол: {self.sex} этап поиска: {self.stage} "
            f"возраст с : {self.age_from} возраст до: {self.age_to} статус: {self.search_status} офсет: {self.offset}"
        )


class Favorites(Base):
    __tablename__ = "favourites"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    vk_user_id = Column(String, primary_key=True, nullable=False)
    
    def __str__(self):
        return f"Избранный пользователь: {self.vk_user_id} id_пользователя_бота: {self.user_id}"


class UserSearchHistory(Base):
    __tablename__ = "user_search_history"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True, nullable=False)
    vk_user_id = Column(String, primary_key=True, nullable=False)
    
    def __str__(self):
        return f"История поиска: {self.id} {self.user_id} {self.vk_user_id}"


class Blacklist(Base):
    __tablename__ = "blacklist"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    banned_user_id = Column(String, nullable=False, primary_key=True)


class UserToken(Base):
    __tablename__ = "user_token"

    user_id = Column(String, ForeignKey("users.id"), unique=True, primary_key=True)
    token = Column(String, nullable=False, primary_key=True)

    user = relationship("Users", back_populates="token")


def create_tables():
    Base.metadata.drop_all(engine_orm)
    Base.metadata.create_all(engine_orm)
