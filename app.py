import os
import vk_api
from chat import Chat
from user import UserMatching, User, UserSearchFilter
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkApi
import re
import vk
from enum import Enum

RE_PARSE_AGE_PARAMS = re.compile(r"(\d{2}).+(\d{2})")
RE_AUTH_TOKEN_PATTERN = re.compile(r"access_token=([^&]*)")
VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")
VK_GROUP_ID = os.getenv("VK_GROUP_ID")


class Stage(Enum):
    FIRST_MESSAGE = 0
    AUTH_REQUESTED = 1
    USER_AUTHORIZED = 2
    AGE_REQUESTED = 3
    SEARCH_LOOP = 4


class Action(Enum):
    CHANGE_AGE_RANGE = "change_age_range"
    NEXT_VARIANT = "next"
    ADD_FAVORITES = "add_to_favorites"
    REMOVE_FAVORITE = "remove_favorite"
    ADD_BLACKLIST = "add_to_blacklist"
    SHOW_FAVORITES = "show_favorites"
    SHOW_HELP = "help"
    LIKE_PHOTO = "like_photo"


class VKinder:
    def __init__(self):
        if not VK_GROUP_ID or not os.getenv("VK_APP_ID"):
            error = vk_api.ApiError(vk=None, method=None, values=None, raw=None, error={
                "error_code": 5,
                "error_msg": (
                    f"{'VK group ID required! ' if not VK_GROUP_ID else ''}"
                    f"{'VK application ID required! ' if not os.getenv('VK_APP_ID') else ''}"
                )
            })
            raise error
        self.chat = Chat(vk_group_id=VK_GROUP_ID, vk_group_token=VK_GROUP_TOKEN)
        self.current_user_session = None
        self.user_sessions = {}

    def get_keyboard(self):
        stage = Stage(self.current_user_session.user.stage)
        if stage == Stage.FIRST_MESSAGE:
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_openlink_button(label="Авторизоваться", link=vk.VK_IMPLICIT_FLOW_URL,
                                         payload={"action": "auth"})
            return keyboard.get_keyboard()
        if stage in [Stage.AGE_REQUESTED, Stage.AUTH_REQUESTED, Stage.USER_AUTHORIZED]:
            return VkKeyboard.get_empty_keyboard()
        if stage == Stage.SEARCH_LOOP:
            keyboard = VkKeyboard()
            keyboard.add_button(label="Следующий вариант ➜", color=VkKeyboardColor.PRIMARY,
                                payload={"ACTION_TYPE": Action.NEXT_VARIANT.value})
            keyboard.add_line()
            keyboard.add_button(label="Изменить возрастной диапазон", color=VkKeyboardColor.SECONDARY,
                                payload={"ACTION_TYPE": Action.CHANGE_AGE_RANGE.value})
            keyboard.add_line()
            keyboard.add_button(label="Показать избранное", color=VkKeyboardColor.SECONDARY,
                                payload={"ACTION_TYPE": Action.SHOW_FAVORITES.value})
            keyboard.add_line()
            keyboard.add_button(label="Помощь", color=VkKeyboardColor.SECONDARY,
                                payload={"ACTION_TYPE": Action.SHOW_HELP.value})
            return keyboard.get_keyboard()

    def greetings(self):
        text = (
            "Мы не знакомы, либо Вы давно не заходили в наш чат, поэтому требуется авторизоваться.\n"
            "Чтобы пройти авторизацию, нажмите на кнопку \"Авторизоваться\" . После подтверждения доступа VK, "
            f"скопируйте ссылку из адресной строки браузера и отправьте её в чат."
        )
        self.chat.reply(text=text, keyboard=self.get_keyboard())
        self.current_user_session.user.stage = Stage.AUTH_REQUESTED

    def show_help(self):
        text = (
            "Вы можете пользоваться не только кнопками, но и писать команды в чат:\n"
            " - введите 0 чтобы изменить возрастной диапазон\n"
            " - введите 1 чтобы перейти к следующему варианту\n"
            " - введите 2 чтобы добавить последний вариант в избранное\n"
            " - введите 3 чтобы добавить последний вариант в черный список\n"
            " - введите 4 чтобы показать избранных пользователей\n"
            " - введите 5 чтобы показать справку\n"
        )
        self.chat.reply(text=text)

    def request_age_range(self):
        self.current_user_session.user.stage = Stage.USER_AUTHORIZED
        self.chat.reply("Укажите возрастной диапозон для поиска, например: 20-30.",
                        keyboard=self.get_keyboard())
        self.current_user_session.user.stage = Stage.AGE_REQUESTED

    def show_favorites(self):
        # todo: добавить функцию, которая получает список избранных пользователей
        # favorite_user_ids = storage.get_favorites(user_id=user_session.user.user_id)
        favorite_user_ids = []
        if not len(favorite_user_ids):
            return self.chat.reply(text="В избранном пока пусто, взгляните на следующий вариант 😉")
        favorite_users = vk.get_user_info(self.chat.vk, ",".join(favorite_user_ids))
        for favorite_user in favorite_users:
            full_name = f"{favorite_user.get('first_name')} {favorite_user.get('last_name')}"
            profile_link = f"https://vk.com/id{favorite_user.get('id')}"
            photos = vk.get_popular_photos(self.chat.vk, favorite_user.get('id'))
            attachments = list(map(vk.get_photo_attachment_link, photos))
            keyboard = VkKeyboard(inline=True)
            for i, attachment in enumerate(attachments):
                keyboard.add_button(label=f"♥ {i + 1} фото", color=VkKeyboardColor.POSITIVE, payload={
                    "ACTION_TYPE": Action.LIKE_PHOTO.value, "PARAMS": {"photo_media_id": attachment}
                })
            keyboard.add_line()
            keyboard.add_button(label="Удалить из избранного", color=VkKeyboardColor.PRIMARY, payload={
                "ACTION_TYPE": Action.REMOVE_FAVORITE.value, "PARAMS": {"user_id": favorite_user.get("id")}
            })
            self.chat.reply(text=f"{full_name}\n{profile_link}", attachments=attachments,
                            keyboard=keyboard.get_keyboard())

    def show_variant(self):
        variant = self.current_user_session.next()
        if not variant:
            self.chat.reply("Варианты не найдены, попробуйте изменить возрастной диапазон.")
            return self.request_age_range()
        variant_user_id = variant.get("id")
        photos = vk.get_popular_photos(self.current_user_session.vk_session, variant_user_id)
        if not len(photos):
            return self.show_variant()
        attachments = list(map(vk.get_photo_attachment_link, photos))
        keyboard = VkKeyboard(inline=True)
        # todo: сделать функцию, которая получает запись из таблицы Favorites
        # is_favorite = storage.get_favorites(user_session.user.user_id, variant_user_id)
        is_favorite = False
        for i, attachment in enumerate(attachments):
            keyboard.add_button(label=f"♥ {i + 1} фото", color=VkKeyboardColor.POSITIVE, payload={
                "ACTION_TYPE": Action.LIKE_PHOTO.value, "PARAMS": {"photo_media_id": attachment}
            })
        keyboard.add_line()
        action_type = Action.REMOVE_FAVORITE if is_favorite else Action.ADD_FAVORITES
        payload = {"ACTION_TYPE": action_type.value, "PARAMS": {"user_id": variant_user_id}}
        keyboard.add_button(label="Удалить из избранного" if is_favorite else "Добавить в избранное",
                            color=VkKeyboardColor.PRIMARY, payload=payload)
        keyboard.add_button(label="В черный список", color=VkKeyboardColor.NEGATIVE,
                            payload={"ACTION_TYPE": Action.ADD_BLACKLIST.value, "PARAMS": {"user_id": variant_user_id}})
        self.chat.reply(f"{variant['first_name']} {variant['last_name']}\nhttps://vk.com/id{variant_user_id}",
                        attachments=attachments, keyboard=keyboard.get_keyboard())
        self.current_user_session.user.stage = Stage.SEARCH_LOOP
        # todo: update user state

    def add_to_favorites(self, favorite_user_id):
        user_info = self.current_user_session.current_variant
        if not user_info or user_info.get("id") != favorite_user_id:
            user_info = vk.get_user_info(self.current_user_session.vk_session, favorite_user_id)
            if not len(user_info):
                return self.chat.reply("Пользователь не найден, не удалось добавить в избранное!")
            user_info = user_info[0]
        search_sex = self.current_user_session.user.search_filter.sex
        full_name = f"{user_info.get('first_name')} {user_info.get('last_name')}"
        # todo: сделать функцию добавления пользователя в избранное (в БД)
        # storage.add_to_favorites(user.user_id, favorite_user_id)
        self.chat.reply(f"{full_name} добавлен{'' if search_sex == 2 else 'а'} в избранное.")

    def add_to_blacklist(self, blacklist_user_id):
        user_info = self.current_user_session.current_variant
        if not user_info or user_info.get("id") != blacklist_user_id:
            user_info = vk.get_user_info(self.current_user_session.vk_session, blacklist_user_id)
            if not len(user_info):
                return self.chat.reply("Пользователь не найден, не удалось добавить в черный список!")
            user_info = user_info[0]
        search_sex = self.current_user_session.user.search_filter.sex
        full_name = f"{user_info.get('first_name')} {user_info.get('last_name')}"
        # todo: сделать функцию добавления пользователя в черный список (в БД)
        # storage.add_to_blacklist(user.user_id, blacklist_user_id)
        self.chat.reply(f"{full_name} добавлен{'' if search_sex == 2 else 'а'} в черный список.")

    def like_photo(self, photo_media_id):
        photo_media_id = photo_media_id.replace("photo", "").split("_")
        if len(photo_media_id) < 2:
            raise Exception("Медиассылка на изображение повреждена")
        owner_id, photo_id = photo_media_id
        user_info = vk.get_user_info(self.current_user_session.vk_session, owner_id)
        full_name = f"{user_info[0].get('first_name')} {user_info[0].get('last_name')}"
        if vk.like_photo(self.current_user_session.vk_session, owner_id=owner_id, photo_id=photo_id):
            self.chat.reply(f"{full_name}: поставлен лайк!")

    # todo: complete function
    def init_user_session(self, user_id) -> UserMatching:
        if user_session := self.user_sessions.get(user_id):
            return user_session
        user = None
        access_token = None
        # todo: add DB functions
        # user = storage.get_user(user_id)
        # access_token = None if not user else storage.get_user_token(user_id)
        if not user:
            user_info = vk.get_user_info(self.chat.vk, user_id)[0]
            user = User(user_id=user_id, first_name=user_info.get("first_name"), last_name=user_info.get("last_name"),
                        stage=Stage.FIRST_MESSAGE)
            user.search_filter = UserSearchFilter(
                city_id=1,  # user_info.get("city").get("id"),
                sex=2 if user_info.get("sex") == 1 else 1,
                age_from=0,
                age_to=0
            )
            user.birth_date = user_info.get("bdate")
        if access_token:
            vk_session = VkApi(token=access_token)
            if vk_session._check_token():
                return UserMatching(current_user=user, vk_session=vk_session)
        user.stage = Stage.FIRST_MESSAGE
        return UserMatching(current_user=user, vk_session=None)

    def run(self):
        for message in self.chat.messages():
            self.current_user_session = self.init_user_session(message.user_id)
            self.user_sessions[message.user_id] = self.current_user_session
            user = self.current_user_session.user
            stage = Stage(user.stage)
            if stage == Stage.AUTH_REQUESTED:
                if access_token := RE_AUTH_TOKEN_PATTERN.findall(message.text):
                    user_vk_session = VkApi(token=access_token[0])
                    if not user_vk_session._check_token():
                        self.chat.reply("Не удалось авторизоваться, попробуйте ещё раз.")
                        user.stage = Stage.FIRST_MESSAGE
                    else:
                        self.current_user_session.vk_session = user_vk_session
                        user.stage = Stage.USER_AUTHORIZED
            if stage == Stage.FIRST_MESSAGE:
                self.greetings()
                user.stage = Stage.AUTH_REQUESTED
                continue
            if stage == Stage.AGE_REQUESTED:
                matches = re.findall(r"^(\d{2})\D+(\d{2})$", message.text)
                if not matches or len(matches[0]) < 2:
                    self.chat.reply("Возраст задан не верно!")
                    self.request_age_range()
                    continue
                age_from, age_to = map(int, matches[0])
                user.search_filter.age_to = age_to
                user.search_filter.age_from = age_from
                user.stage = Stage.SEARCH_LOOP
                self.show_help()
                self.chat.reply(text=f"Начинаю поиск в возрасте от {age_from} до {age_to}...",
                                keyboard=self.get_keyboard())
                self.show_variant()
                continue
            action_type = None
            action_params = None
            if payload := message.payload:
                action_type = Action(payload.get("ACTION_TYPE"))
                action_params = payload.get("PARAMS")
            if not action_type:
                stage = Stage(user.stage)
                if stage == Stage.USER_AUTHORIZED or message.text == "0":
                    action_type = Action.CHANGE_AGE_RANGE
                elif message.text == "1":
                    action_type = Action.NEXT_VARIANT
                elif message.text == "2":
                    action_type = Action.ADD_FAVORITES
                    action_params = {"user_id": self.current_user_session.current_variant.get("id")}
                elif message.text == "3":
                    action_type = Action.ADD_BLACKLIST
                    action_params = {"user_id": self.current_user_session.current_variant.get("id")}
                elif message.text == "4":
                    action_type = Action.SHOW_FAVORITES
                elif message.text == "5":
                    action_type = Action.SHOW_HELP
            if action_type == Action.SHOW_HELP:
                self.show_help()
            elif action_type == Action.SHOW_FAVORITES:
                self.show_favorites()
            elif action_type == Action.NEXT_VARIANT:
                self.show_variant()
            elif action_type == Action.CHANGE_AGE_RANGE:
                self.request_age_range()
                self.current_user_session.clear_variants()
            elif action_type == Action.ADD_FAVORITES:
                self.add_to_favorites(action_params.get("user_id"))
            elif action_type == Action.ADD_BLACKLIST:
                self.add_to_blacklist(action_params.get("user_id"))
            elif action_type == Action.LIKE_PHOTO:
                self.like_photo(action_params.get("photo_media_id"))
