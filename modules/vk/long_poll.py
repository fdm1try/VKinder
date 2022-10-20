import requests
import api_raw
from enum import Enum

LONG_POLL_API_VERSION = '5.131'


class Mode(Enum):
    ReceiveAttachments = 2,
    ExtendedEvents = 8,
    ReceivePTS = 32,
    ReceiveExtraOnUserOnlineEvent = 64,
    ReceiveRandomID = 128


class MessageFlag(Enum):
    Unread = 1,
    Outbox = 2,
    Replied = 4,
    Important = 8,
    Chat = 16,
    Friends = 32,
    SPAM = 64,
    Deleted = 128,
    Fixed = 256,
    Media = 512,
    Hidden = 65536,
    DeleteForAll = 131072,
    NotDelivered = 262144


class Event:
    def __init__(self, event_id, *args):
        self.event_id = event_id
        self.params = list(args)

    def __str__(self):
        return f'ID: {str(self.event_id)}, params: {",".join([str(param) for param in self.params])}'


class EventNewMessage(Event):
    def __init__(self, message_id: int, flags: int, minor_id: int, *extra_fields):
        super().__init__(4)
        self.message_id = message_id
        self.flags = flags
        self.minor_id = minor_id
        self.extra_fields = list(extra_fields)
        self._timestamp = self.extra_fields[0] if len(self.extra_fields) else None
        self._text = self.extra_fields[1] if len(self.extra_fields) > 1 else None

    def __str__(self):
        return (f'New message with id {self.message_id} and flags {self.flags}.'
                f'Extra fields: {",".join([str(field) for field in self.extra_fields])}')

    def _load_message_data(self):
        data = api_raw.Messages.get_by_id(message_ids=[self.message_id])
        self._from_id = data.get('from_id')
        self._timestamp = data.get('date')
        self._text = data.get('text')

    @property
    def text(self):
        if not self._text:
            self._load_message_data()
        return self._text

    @property
    def timestamp(self):
        if not self._timestamp:
            self._load_message_data()
        return self._timestamp

    @property
    def sender(self):
        if not self._from_id:
            self._load_message_data()
        return self._from_id


def _parse_event(*args) -> Event:
    event_id = args[0]
    if event_id == 4:
        return EventNewMessage(*args[1:])
    return Event(*args)


class LongPoll:
    def __init__(self, community_token, group_id, wait_for_answer: int = 25, *modes):
        self.mode = sum(modes)
        self.wait_for_answer = 90 if wait_for_answer > 90 else wait_for_answer
        data = api_raw.Messages.get_long_poll_server(community_token, group_id, api_raw.API_VERSION)
        self._server = data.get('server')
        self._ts = data.get('ts')
        self._key = data.get('key')

    def __iter__(self):
        self._events = []
        self._cursor = 0
        return self

    def __next__(self):
        if self._cursor < len(self._events):
            event = self._events[self._cursor]
            self._cursor += 1
            return event
        try:
            response = requests.get(f'https://{self._server}', params={
                'act': 'a_check',
                'ts': self._ts,
                'key': self._key,
                'wait': self.wait_for_answer,
                'mode': self.mode,
                'version': LONG_POLL_API_VERSION
            }, timeout=self.wait_for_answer)
        except requests.exceptions.ReadTimeout:
            raise StopIteration
        if response.status_code != 200:
            raise Exception(f'HTTP error, code: {response.status_code}')
        data = response.json()
        self._ts = data.get('ts')
        for update in data.get('updates'):
            self._events.append(_parse_event(*update))
        if self._cursor < len(self._events):
            event = self._events[self._cursor]
            self._cursor += 1
            return event
        raise StopIteration

    def event_loop(self):
        while True:
            for event in self:
                yield event
