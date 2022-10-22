import vk_api
import token_and_id
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType


token = token_and_id.token
user_id = token_and_id.user_id

vk_session = vk_api.VkApi(token=token)
vk_session._auth_token()
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

def send(ui, message, attachment=None):
    vk_session.method("messages.send", {"user_id": ui, "message": message, "random_id": get_random_id(),
                                        "attachment": attachment})

def search():
    result = vk_session.method("users.search", {"count": 100, "sex": req_sex, "city_id": req_city_id,
                                                "age_from": age_from, "age_to": age_to,"status": 1 or 6,
                                                "has_photo": 1, "fields": "city"})
    return result



def make_offer(i):
    try:
        choice_id = choice['items'][i]['id']
        choice_name = choice['items'][i]['first_name']
        choice_surname = choice['items'][i]['last_name']
        choices.append(choice_id)
        return send(event.user_id, f"Вот такой вариант:\n\n{choice_name} {choice_surname}\n"
                                   f"https://vk.com/id{choice_id}\n\n1 - добавить в Избранное\n"
                                   f"0 - просмотреть Избранное\nПоискать ещё? (Да/Нет)\n")
    except IndexError:
        send(event.user_id, "Похоже больше я не смогу ничего найти.\n"
                            "0 - просмотреть Избранное")

def show_all_favourites():
    for favourite in favourites:
        favourite_info = vk_session.method("users.get", {"user_ids": favourite})
        favourite_name = favourite_info[0]['first_name']
        favourite_surname = favourite_info[0]['last_name']
        send(event.user_id, f'{favourite_name} {favourite_surname}\nhttps://vk.com/id{favourite}\n')

def get_user_info(id):
    user_info = vk_session.method("users.get", {"user_ids": id, "fields": "city, sex"})
    return user_info


if __name__ == "__main__":
    # try:
        choices = []
        favourites = []
        user_info = get_user_info(user_id)
        req_city_id = user_info[0]['city']['id']
        if user_info[0]['sex'] == 1:
            req_sex = 2
        elif user_info[0]['sex'] == 2:
            req_sex = 1

        send(user_id, "Привет!\nМеня зовут VKinder, и я - бот для поиска пары.\n"
                      "Укажи интересующий тебя возрастной диапазон\n"
                      "В формате '18 99', где:\n18 - минимальный возраст,\n99 - максимальный возраст")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                try:
                    i = 0
                    words = event.text.split()
                    age_from = int(words[0])
                    age_to = int(words[1])
                    choice = search()
                    send(user_id, f"Ок. Буду искать не моложе {age_from} и не старше {age_to} лет.\n"
                                  f"Начинаем(Да/Нет)")
                    while True:
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW:
                                if event.text.lower() == 'да':
                                    send(event.user_id, "Ищу...")
                                    choice = search()
                                    if choice['count'] == 0:
                                        send(event.user_id, "Знаешь, по таким критериям я никого найти не смогу. Увы")
                                        break
                                    else:
                                        choice_id = choice['items'][i]['id']
                                        if choice_id in choices:
                                            i += 1
                                        make_offer(i)
                                elif event.text.lower() == '1':
                                    send(event.user_id, "Добавляю в Избранное...\n\n""0 - просмотреть Избранное"
                                                        "\nПоискать ещё? (Да/Нет)")
                                    favourites.append(choice['items'][i]['id'])
                                elif event.text.lower() == '0':
                                    send(event.user_id, "Избранное:\n")
                                    show_all_favourites()
                                    send(event.user_id, "\nПоискать ещё? (Да/Нет)")
                                elif event.text.lower() == 'нет':
                                    send(event.user_id, "Поиск остановлен.Да - поиск\n 0 - просмотреть Избранное")



                except Exception as ex:
                    print(ex)
'''Пытаюсь убрать капчу'''
    # except vk_api.exceptions.Captcha as captcha:
    #     key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
    #     captcha.try_again(key)
