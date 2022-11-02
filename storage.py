import bot_db_tables as db
from typing import List
from bot_db_tables import Users, User_search_history, Favourites
from user import User, UserSearchFilter

def add_user(user:User) -> User:
    user_id = user.user_id
    stage = user.stage
    city_id = user.search_filter.city_id
    sex = user.search_filter.sex
    age_from = user.search_filter.age_from
    age_to = user.search_filter.age_to
    search_status = user.search_filter.status
    offset = user.search_filter.offset
    """Метод добавляет пользователя чат-бота в таблицу Users

    Args:
        user: экземпляр класса User
        
    """
    
    user =Users(id = user_id, city_id=city_id, sex=sex, stage = stage, age_from=age_from, age_to=age_to, search_status=search_status, offset=offset)
    with db.Session_orm() as session:
        if session.query(Users).filter(Users.id==user_id).all():
            print("Пользователь с таким id уже существует в базе данных")
        else: session.add(user), session.commit()


def search_user(user_id: int) -> User:
    
    """Метод осуществляет поиск пользователя чат-бота в таблице Users по заданному user_id

    Args:
        user_id (int): идентификатор пользователя.

    Returns:
        Метод возвращает одну запись с данными о пользователе из таблицы Users (данные экземпляра класса User)
    """
    
    with db.Session_orm() as session:   
        print(session.query(Users).filter(Users.id == user_id).one())
        
def update_user(user:User) -> User:
    user_id = user.user_id
    stage = user.stage
    city_id = user.search_filter.city_id
    sex = user.search_filter.sex
    age_from = user.search_filter.age_from
    age_to = user.search_filter.age_to
    search_status = user.search_filter.status
    offset = user.search_filter.offset
    
    """Метод обновляет данные о пользователе в таблице Users
    Args:
        Args:
        user: экземпляр класса User
        
    """

    with db.Session_orm() as session:
        session.query(Users).filter(Users.id == user_id).update({'city_id': city_id, 'sex': sex, 'stage': stage,
        'age_from': age_from, 'age_to': age_to, 'search_status': search_status, 'offset': offset}, synchronize_session = False)
        session.commit()

def add_favourite(user:User, favourites: List[int]) -> None:
    user_id = user.user_id
    """Метод добавляет понравившегося пользователя vk в таблицы Favourites и User_search_history БД

    Args:
        favourites (List[int]): список всех понравившихся пользователей.
    """
   
    for favourite in favourites:
        with db.Session_orm() as session:
            favourite_user = Favourites(vk_user_id = favourite, user_id=user_id)
            user_history = User_search_history(user_id = user_id,vk_user_id = favourite)
            session.add_all([favourite_user, user_history]), session.commit()
        
def search_favourite(vk_user_id):
    """Метод осуществляет поиск понравившегося пользователя в таблице Favourites по введенному идентификатору - vk_user_id

    Args:
        vk_user_id (_type_): идентификатор избранного пользователя vk.
        
    Returns:
        Метод возвращает все записи с данными о пользователе vk из таблицы Favourites.
    """
   
    with db.Session_orm() as session:
        for variant in session.query(Favourites).filter(Favourites.vk_user_id == vk_user_id).all():
            print(variant)

def delete_favourite(vk_user_id) -> None:
    """Метод удаляет избранного пользователя из таблиц Favourites и User_search_history

    Args:
        vk_user_id (_type_): идентификатор пользователя vk.
    """
    with db.Session_orm() as session:
        session.query(Favourites).filter(Favourites.vk_user_id == vk_user_id).delete(synchronize_session=False)
        session.query(User_search_history).filter(User_search_history.vk_user_id == vk_user_id).delete(synchronize_session=False)
        session.commit()
        
# user1 = User(user_id=12345, first_name='Иван', last_name='Иванов')       
# user1.search_filter = UserSearchFilter(city_id=1, sex=1, age_from=20, age_to = 25)
# user2 = User(user_id=12346, first_name='Игорь', last_name='Петров')       
# user2.search_filter = UserSearchFilter(city_id=2, sex=1, age_from=20, age_to = 25)
# favourites=[12345]
# delete_favourite(12345)
