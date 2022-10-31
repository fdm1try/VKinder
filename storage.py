import bot_db_tables as db
from typing import List
from bot_db_tables import Users, User_search_history, Favourites
from sqlalchemy.sql import exists   

def add_user_todb(self, search_status: int = 6, offset: int = 0, session = db.Session.orm) -> None:
    """Метод добавляет пользователя чат-бота в таблицу Users

    Args:
        search_status (int, optional): статус поиска, по умолчанию задаем 6 (принимает значения 1 или 6).
        offset (int, optional): параметр поиска. По умолчанию 0.
        session (_type_, optional): специальный объект - сессия, для подключения к БД.
    """
    
    user =Users(id = self.user_id, city_id=self.search_filter.city_id, sex=self.search_filter.sex, stage = self.stage, 
    age_from=self.search_filter.age_from, age_to=self.search_filter.age_to, search_status=self.search_status, offset=self.offset)
    if not session.query(exists().where(Users.id == self.user_id)).all():
        with session():
            session.add(user)
    
    
def search_user(self, user_id: int, session = db.Session.orm) -> Query:
    """Метод осуществляет поиск пользователя чат-бота в таблице Users по заданному user_id

    Args:
        user_id (int): идентификатор пользователя.
        session (_type_, optional): специальный объект - сессия, для подключения к БД.

    Returns:
        Метод возвращает одну запись с данными о пользователе из таблицы Users
    """
    
    with session():
       return session.query(Users).filter(Users.id == self.user_id).one()
    
def update_user(self,city_id: int, sex: int, stage: int, age_from: int, age_to: int,
                search_status:int, offset: int,  session = db.Session.orm) -> None:
    """Метод обновляет данные о пользователе в таблице Users

    Args:
        city_id (int): идентификатор города.
        sex (int): пол пользователя чат-бота (1 или 2).
        stage (int): этап поиска, на котором находится пользователь.
        age_from (int): возраст, с которого необходимо начать поиск.
        age_to (int): возрастная граница окончания поиска.
        search_status (int): статус поиска (1 или 6).
        offset (int): параметр поиска.
        session (_type_, optional): специальный объект - сессия, для подключения к БД.
    """

    with session():
        session.query(Users).filter(Users.id == self.user_id).update({'city_id': self.city_id, 'sex': self.sex, 'stage': self.stage,
        'age_from': self.age_from, 'age_to': self.age_to, 'search_status': self.search_status, 'offset': self.offset}, synchronize_session = False)
        
def add_favourite(self, favourites: List[int], session = db.Session.orm) -> None:
    """Метод добавляет понравившегося пользователя vk в таблицы Favourites и User_search_history БД

    Args:
        favourites (List[int]): список всех понравившихся пользователей.
        session (_type_, optional): специальный объект - сессия, для подключения к БД.
    """
   
    for favourite in favourites:
        favourite_user = Favourites(vk_user_id = favourite, user_id=self.user_id)
        user_history = User_search_history(user_id = self.user_id,vk_user_id = favourite)
        with session():
            session.add([favourite_user, user_history])
        
def search_favourite(favourites, vk_user_id,session = db.session.orm) -> Query:
    """Метод осуществляет поиск понравившегося пользователя в таблице Favourites по введенному идентификатору - vk_user_id

    Args:
        vk_user_id (_type_): идентификатор избранного пользователя vk.
        session (_type_, optional): специальный объект - сессия, для подключения к БД.
        
    Returns:
        Метод возвращает все записи с данными о пользователе vk из таблицы Favourites.
    """
   
    with session():
        return session.query(Favourites).filter(Favourites.vk_user_id == favourites['vk_user_id']).all()

def delete_favourite(vk_user_id,session = db.Session.orm) -> None:
    """Метод удаляет избранного пользователя из таблиц Favourites и User_search_history

    Args:
        vk_user_id (_type_): идентификатор пользователя vk.
        session (_type_, optional): специальный объект - сессия, для подключения к БД.
    """
    with session():
        session.query(Favourites).filter(Favourites.vk_user_id == vk_user_id).delete(synchronize_session=False)
        session.query(User_search_history).filter(User_search_history.vk_user_id == vk_user_id).delete(synchronize_session=False)        