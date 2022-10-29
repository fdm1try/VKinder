import os
import pytest
from vk_api import VkApi
from user import User, UserMatching, UserSearchFilter
import vk
from datetime import date


@pytest.fixture()
def age_params():
    return [
        (20, 40, True),
        (40, 39, None),
        (30, 30, True)
    ]


@pytest.fixture(scope='session')
def vk_user():
    vk = VkApi(token=os.getenv('USER_TOKEN'))
    vk.get_api()
    return vk


def pest_vk_get_user_info(vk_user):
    user = vk.get_user_info(vk_user, user_id=None)[0]
    assert 'id' in user and isinstance(user.get('id'), int)
    assert 'sex' in user and isinstance(user.get('sex'), int)
    assert 'first_name' in user and 'last_name' in user
    assert 'city' in user and 'id' in user['city'] and isinstance(user['city']['id'], int)
    assert not user['is_closed']
    pass


def pest_vk_get_popular_photos(vk_user):
    photos = vk.get_popular_photos(vk_user, 1)
    all_photos = vk_user.method('photos.get', {'count': 1000, 'owner_id': 1, 'album_id': 'profile', 'extended': 1})
    sorted_photos = [photo for photo in sorted(all_photos['items'], key=lambda item: item['likes']['count'],
                                               reverse=True)]
    assert photos == list(sorted_photos[:3])


def pest_vk_get_open_user_pages(vk_user):
    def verify_user(user, from_age, to_age):
        assert 'first_name' in user and 'last_name' in user
        assert isinstance(user['id'], int)
        birth_date = date(*list(map(int, reversed(user['bdate'].split('.')))))
        user_age = vk.age(birth_date)
        assert from_age <= user_age < to_age + 1

    user_list = vk.get_open_user_pages(vk=vk_user, city_id=1, sex=1, age_from=20, age_to=30, count=1000)
    for user in user_list:
        verify_user(user, from_age=20, to_age=30)
    user_list = vk.get_open_user_pages(vk=vk_user, city_id=1, sex=1, age_from=30, age_to=30, count=1000)
    assert len(user_list)
    for user in user_list:
        verify_user(user, from_age=30, to_age=30)
    user_list = vk.get_open_user_pages(vk=vk_user, city_id=1, sex=1, age_from=31, age_to=30, count=1000)
    assert user_list is None


def pest_user_search_filter():
    search_filter = UserSearchFilter(city_id=1, sex=1, age_from=20, age_to=60)
    assert search_filter.status == 6
    search_filter.status = 1
    search_filter.offset = 100
    assert search_filter.offset == 100 and search_filter.status == 1
    search_filter.city_id = 2
    assert search_filter.status == 6 and search_filter.offset == 0
    search_filter.offset = 100
    search_filter.status = 1
    assert search_filter.status == 1 and search_filter.offset == 0
    search_filter.offset = 20
    assert search_filter.offset == 20
    search_filter.age_to = 30
    assert search_filter.age_to == 30 and search_filter.offset == 0
    search_filter.offset = 20
    search_filter.age_from = 30
    assert search_filter.age_from == 30 and search_filter.offset == 0


def test_user_matching(vk_user, age_params):
    for params in age_params:
        from_age, to_age, expected_result = params
        search_filter = UserSearchFilter(city_id=1, sex=1, age_from=from_age, age_to=to_age)
        current_user = vk.get_user_info(vk_user, None)[0]
        user = User(user_id=current_user['id'], first_name=current_user.get('first_name'),
                    last_name=current_user.get('last_name'), search_filter=search_filter)
        user_matching = UserMatching(vk_user, user)
        history = []
        if expected_result is None:
            assert user_matching.next() is None
            return
        while variant := user_matching.next():
            assert variant['id'] not in history
            history += [variant['id']]
            birth_date = date(*list(map(int, reversed(variant['bdate'].split('.')))))
            user_age = vk.age(birth_date)
            assert from_age <= user_age < to_age + 1





