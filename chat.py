import vk
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent
import json


class Message:
    def __init__(self, peer_id, text, payload=None, event_data=None):
        self.peer_id = peer_id
        self.text = text
        self.event_data = event_data
        self.payload = payload

    @property
    def user_id(self):
        if isinstance(self.event_data, VkBotMessageEvent):
            return self.event_data.message.get('from_id')

    @staticmethod
    def from_bot_event(event: VkBotMessageEvent):
        payload = json.loads(event.message.get("payload")) if "payload" in event.message else None
        return Message(peer_id=event.message.peer_id, text=event.message.text, payload=payload, event_data=event)


class Chat:
    def __init__(self, vk_group_id, vk_group_token):
        self.vk = VkApi(token=vk_group_token)
        self._longpoll = VkBotLongPoll(self.vk, vk_group_id)
        self.current_message: Message | None = None

    def messages(self):
        for event in self._longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.current_message = Message.from_bot_event(event)
                yield self.current_message

    def reply(self, text: str, attachments: list = None, keyboard=None):
        vk.send_message(self.vk, peer_id=self.current_message.peer_id, message=text, attachments=attachments,
                        keyboard=keyboard)
