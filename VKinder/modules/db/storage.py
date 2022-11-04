from VKinder.modules.db import model
from VKinder.modules.user import User, UserSearchFilter
from enum import Enum


def add_user(user: User) -> bool:
    user_id = str(user.user_id)
    stage = user.stage.value if isinstance(user.stage, Enum) else user.stage
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
    
    user = model.Users(id=user_id, city_id=city_id, sex=sex, stage=stage, age_from=age_from, age_to=age_to,
                 search_status=search_status, offset=offset)
    with model.Session_orm() as session:
        if session.query(model.Users).filter(model.Users.id == user_id).all():
            return False
        session.add(user)
        session.commit()
        return True


def get_user(user_id) -> User | None:
    with model.Session_orm() as session:
        user = session.query(model.Users).filter(model.Users.id == str(user_id)).first()
        if not user:
            return None
        return User(user_id=user.id, first_name=None, last_name=None, stage=user.stage,
                    search_filter=UserSearchFilter(city_id=user.city_id, age_from=user.age_from, age_to=user.age_to,
                                                   offset=user.offset, status=user.search_status, sex=user.sex))


def update_user(user: User) -> bool:
    with model.Session_orm() as session:
        if item := session.query(model.Users).filter(model.Users.id == str(user.user_id)).first():
            item.stage = user.stage.value if isinstance(user.stage, Enum) else user.stage
            item.city_id = user.search_filter.city_id
            item.age_from = user.search_filter.age_from
            item.age_to = user.search_filter.age_to
            item.sex = user.search_filter.sex
            item.offset = user.search_filter.offset
            item.search_status = user.search_filter.status
            session.commit()
            return True
        return False


def add_favorite(user_id, favorite_user_id) -> bool:
    """Метод добавляет понравившегося пользователя vk в таблицу Favourites

    Args:
        user_id (_type_): идентификатор пользователя vk (пользователь чат-бота).
        favorite_user_id (_type_): идентификатор пользователя vk, добавляемого в избранное.
    """
    filters = [model.Favorites.user_id == str(user_id), model.Favorites.vk_user_id == str(favorite_user_id)]
    with model.Session_orm() as session:
        if session.query(model.Favorites).filter(*filters).first():
            return False
        session.add(model.Favorites(vk_user_id=str(favorite_user_id), user_id=str(user_id)))
        session.commit()
        return True


def get_favorites(user_id, favorite_user_id=None) -> list | bool:
    filters = [model.Favorites.user_id == str(user_id)]
    if favorite_user_id:
        filters += [model.Favorites.vk_user_id == str(favorite_user_id)]
    with model.Session_orm() as session:
        favorites = session.query(model.Favorites).filter(*filters).all()
        if favorite_user_id is not None:
            return bool(len(favorites))
        return [entry.vk_user_id for entry in favorites]


def delete_favorite(user_id, vk_user_id):
    """Метод удаляет избранного пользователя из таблиц Favourites и User_search_history

    Args:
        user_id (_type_): идентификатор пользователя vk (пользователь чат-бота).
        vk_user_id (_type_): идентификатор пользователя vk из списка избранных.
    """
    with model.Session_orm() as session:
        filters = [model.Favorites.vk_user_id == str(vk_user_id), model.Favorites.user_id == str(user_id)]
        if entry := session.query(model.Favorites).filter(*filters).first():
            session.delete(entry)
            session.commit()
            return True
        return False


def add_to_blacklist(user_id, banned_user_id):
    with model.Session_orm() as session:
        if session.query(model.Blacklist).filter(
                model.Blacklist.user_id == str(user_id), model.Blacklist.banned_user_id == str(banned_user_id)
        ).first():
            return False
        session.add(model.Blacklist(user_id=str(user_id), banned_user_id=str(banned_user_id)))
        session.commit()
        return True


def get_blacklist(user_id, banned_user_id=None) -> list | bool:
    filters = [model.Blacklist.user_id == str(user_id)]
    if banned_user_id:
        filters += [model.Blacklist.banned_user_id == str(banned_user_id)]
    with model.Session_orm() as session:
        blacklist = session.query(model.Blacklist).filter(*filters).all()
        if banned_user_id is not None:
            return bool(len(blacklist))
        return [entry.banned_user_id for entry in blacklist]


def get_user_token(user_id) -> str:
    with model.Session_orm() as session:
        if user := session.query(model.UserToken).filter(model.UserToken.user_id == str(user_id)).first():
            return user.token


def set_user_token(user_id, token: str) -> bool:
    with model.Session_orm() as session:
        if user := session.query(model.UserToken).filter(model.UserToken.user_id == str(user_id)).first():
            user.token = token
        else:
            session.add(model.UserToken(user_id=str(user_id), token=token))
        session.commit()
        return True


def add_to_history(user_id, visited_user_id) -> bool:
    filters = [model.UserSearchHistory.user_id == str(user_id),
               model.UserSearchHistory.vk_user_id == str(visited_user_id)]
    with model.Session_orm() as session:
        if session.query(model.UserSearchHistory).filter(*filters).first():
            return False
        session.add(model.UserSearchHistory(user_id=str(user_id), vk_user_id=str(visited_user_id)))
        session.commit()
        return True


def get_history(user_id, visited_user_id=None) -> list | bool:
    filters = [model.UserSearchHistory.user_id == str(user_id)]
    if visited_user_id is not None:
        filters += [model.UserSearchHistory.vk_user_id == str(visited_user_id)]
    with model.Session_orm() as session:
        history = session.query(model.UserSearchHistory).filter(*filters).all()
        if visited_user_id is not None:
            return bool(len(history))
        return [entry.vk_user_id for entry in history]


def delete_from_history(user_id, visited_user_id=None):
    filters = [model.UserSearchHistory.user_id == str(user_id)]
    if visited_user_id is not None:
        filters += [model.UserSearchHistory.vk_user_id == str(visited_user_id)]
    with model.Session_orm() as session:
        session.query(model.UserSearchHistory).filter(*filters).delete(synchronize_session=False)
        session.commit()


def init():
    try:
        with model.Session_orm() as session:
            (
                session.query(model.Users)
                .join(model.Favorites, model.Users.id == model.Favorites.user_id)
                .join(model.UserSearchHistory, model.Users.id == model.UserSearchHistory.user_id)
                .join(model.Blacklist, model.Users.id == model.Blacklist.user_id)
                .join(model.UserToken, model.Users.id == model.UserToken.user_id)
            ).first()
            return True
    except Exception as err:
        return False
