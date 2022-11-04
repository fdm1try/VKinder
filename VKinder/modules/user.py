import vk_api
from VKinder.modules import vk


class UserSearchFilter:
    def __init__(self, city_id: int, sex: int, age_from: int, age_to: int, status: int = 6, offset: int = 0):
        self._city_id = city_id
        self._age_from = age_from
        self._age_to = age_to
        self._status = status
        self.offset = offset
        self.sex = sex

    @property
    def city_id(self):
        return self._city_id

    @city_id.setter
    def city_id(self, city_id: int):
        self.reset_offset()
        self._city_id = city_id

    @property
    def age_from(self):
        return self._age_from

    @age_from.setter
    def age_from(self, age: int):
        self.reset_offset()
        self._age_from = age

    @property
    def age_to(self):
        return self._age_to

    @age_to.setter
    def age_to(self, age: int):
        self.reset_offset()
        self._age_to = age

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        self._status = new_status
        self.offset = 0

    def reset_offset(self):
        self._status = 6
        self.offset = 0


class User:
    def __init__(self, user_id, first_name: str, last_name: str, stage=0,
                 search_filter: UserSearchFilter = None):
        self._variants = []
        self.stage = stage
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.search_filter = search_filter
        self.birth_date = None

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        if self.birth_date:
            return vk.age(self.birth_date)


class UserMatching:
    def __init__(self, vk_session: vk_api, current_user: User):
        self._variants = []
        self._history = []
        self._current_variant = None
        self.vk_session = vk_session
        self.user = current_user

    @property
    def current_variant(self):
        return self._current_variant or vk.get_user_info(self.vk_session, self._history[-1])[0]

    @property
    def history(self):
        return self._history[:]

    @history.setter
    def history(self, history: list):
        self._history = history

    def clear_variants(self):
        self._variants = []

    def next(self):
        if self._variants is None:
            if self.user.search_filter.status == 6:
                self.user.search_filter.status = 1
                self._variants = []
                return self.next()
            return None
        while self._variants and len(self._variants):
            variant = self._variants.pop(0)
            self.user.search_filter.offset += 1
            if variant["id"] not in self._history:
                self._history.append(variant["id"])
                self._current_variant = variant
                return variant
        params = self.user.search_filter
        if not (params and params.city_id and params.sex and params.age_from and params.age_to and params.status):
            raise Exception("Фильтры поиска не заполнены!")
        self._variants = vk.get_open_user_pages(vk=self.vk_session, count=1000, city_id=params.city_id,
                                                sex=params.sex, age_from=params.age_from, age_to=params.age_to,
                                                status=params.status, offset=params.offset)
        return self.next()

    def reset(self):
        self.user.search_filter.reset_offset()
        self._variants = []
