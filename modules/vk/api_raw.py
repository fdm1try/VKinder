import requests
import api_error

API_VERSION = '5.81'
BASE_URI = 'https://api.vk.com/method/{}'


def is_error(response: requests.Response, silent: bool = False) -> int:
    if response.status_code != 200:
        return response.status_code
    data = response.json()
    if error := data.get('error'):
        exception = api_error.ERROR_MAP.get(error.get('error_code'))
        if not exception:
            raise Exception(f'Unmapped VK API Exception with code: {error.get("error_code")}. {error.get("error_msg")}')
        msg = f'{error.get("error_msg")}\n{exception.__doc__.strip()}'
        raise exception(msg)


def api_get(method, **params):
    response = requests.get(BASE_URI.format(method), params={
        **params,
        'v': API_VERSION
    })
    if not is_error(response):
        return response.json().get('response')


class Messages:
    @staticmethod
    def get_long_poll_server(access_token: str, group_id, lp_version: float) -> dict:
        """
        :param access_token: community token
        :param group_id: community ID
        :param lp_version: version for connecting to LongPoll
        :return: Returns an object that contains the fields key, server, ts. Using this data,
        you can connect to the quick message server to instantly receive incoming messages and other events.
        """
        return api_get('messages.getLongPollServer',
                       access_token=access_token, group_id=group_id, lp_version=lp_version)

    @staticmethod
    def get_by_id(message_ids: list, preview_length: int = None, extended: bool = None, fields: list = None,
                  group_id: str = None):
        """
        :param message_ids: Message IDs. Maximum of 100 IDs.
        :param preview_length: The number of characters to trim the message by.
        :param extended: True - return additional fields.
        :param fields: A list of additional fields for users and communities.
        :param group_id: Community ID (for community messages with the user's access key).
        :return: After successful execution, it returns an object containing the number of results in the count field
            and an array of objects describing messages in the items field.
        """
        message_ids = ','.join(message_ids)
        fields = ','.join(fields) if fields and len(fields) else None
        extended = int(extended) if extended else 0
        return api_get('messages.getById', message_ids=message_ids, preview_length=preview_length, extended=extended,
                       fields=fields, group_id=group_id)
