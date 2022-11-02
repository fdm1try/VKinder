import os
import re
from vk_api import VkApi, VkUserPermissions
from vk_api.utils import get_random_id
from vk_api.tools import VkTools
from datetime import date

RE_RU_DATE = re.compile(r"^\d{1,2}\.\d{1,2}\.\d{4}$")

VK_APP_ID = os.getenv("VK_APP_ID")
VK_REQUIRED_USER_PERMISSIONS = (
        VkUserPermissions.OFFLINE | VkUserPermissions.FRIEND | VkUserPermissions.PHOTOS | VkUserPermissions.WALL
)
VK_IMPLICIT_FLOW_URL = (
    f"https://oauth.vk.com/authorize?client_id={VK_APP_ID}&scope={VK_REQUIRED_USER_PERMISSIONS}"
    "&redirect_uri=https://oauth.vk.com/blank.html&response_type=token&state=randomstring"
)


def age(d: date):
    today = date.today()
    years = today.year - d.year
    day = d.day
    if d.month == 2 and day == 29 and not (today.year % 4 == 0 and (today.year % 100 != 0 or today.year % 400 == 0)):
        day = 28
    diff = today - date(today.year, d.month, day)
    return years + (diff.days / 366)


def get_user_info(vk: VkApi, user_id):
    return vk.method("users.get", {"user_ids": user_id, "fields": "city, sex, bdate"})


def get_popular_photos(vk: VkApi, user_id, count=3):
    vk_tools = VkTools(vk)
    photos = vk_tools.get_all(method="photos.get", max_count=1000, values={
        "owner_id": user_id, "album_id": "profile", "extended": 1
    })
    try:
        photos["items"] += vk_tools.get_all(method="photos.getUserPhotos", max_count=1000, values={
            "user_id": user_id, "count": 1000, "extended": 1
        })["items"]
    except Exception:
        pass
    return list(sorted(photos["items"], key=lambda x: x["likes"]["count"], reverse=True)[:count])


def get_open_user_pages(vk: VkApi, city_id, sex, age_from: int, age_to: int, status=6, count=10, offset=0):
    """
    :param vk:
    :param city_id: id города
    :param sex: пол 1 - женский, 2 - мужской
    :param age_from: начало возрастного диапазона
    :param age_to: конец возрастного диапазона
    :param status: 6 по умолчанию - в активном поиске, 0 - любой
    :param count: количество для выборки до фильтрации
    :param offset: смещение для выборки до фильтрации
    :return: в результате может вернуть пустой массив, так как все найденные профили могут быть пустыми
    """
    users = vk.method("users.search", {
        "city": city_id,
        "sex": sex,
        "sort": 0,
        "age_from": age_from,
        "age_to": age_to,
        "status": status,
        "count": count,
        "offset": offset,
        "fields": "bdate"
    })
    items = users.get("items")
    if not len(items):
        return None
    result = []
    for user in items:
        if not user["can_access_closed"]:
            continue
        if "bdate" not in user or not RE_RU_DATE.match(user["bdate"]):
            continue
        birth_date = date(*list(map(int, reversed(user["bdate"].split(".")))))
        user_age = age(birth_date)
        if age_from <= user_age < age_to + 1:
            result.append(user)
    return result


def send_message(vk: VkApi, message, attachments: list = [], chat_id=None, peer_id=None, user_id=None,
                 reply_to=None, keyboard=None):
    result = vk.method("messages.send", {
        "user_id": user_id,
        "chat_id": chat_id,
        "peer_id": peer_id,
        "message": message,
        "random_id": get_random_id(),
        "attachment": ",".join(attachments) if attachments else None,
        "keyboard": keyboard,
        "reply_to": reply_to
    })
    return result


def like_photo(vk: VkApi, owner_id, photo_id):
    result = vk.method("likes.add", {
        "type": "photo",
        "owner_id": owner_id,
        "item_id": photo_id
    })
    return result.get("likes")


def get_photo_attachment_link(photo):
    if "owner_id" not in photo or "id" not in photo:
        return None
    return f"photo{photo['owner_id']}_{photo['id']}"
