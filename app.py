import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk import get_user_info, send_message, get_popular_photos, get_photo_attachment_link
from user import User, UserMatching, UserSearchFilter


COMMUNITY_TOKEN = 'vk1.a.FNxhPBrA2myefi0ar0zkjMNvrVqjdJRsKe8HdOUB-PAEPezzyYs0lmE0gi3VFntD45VB_uxOZPaPkyc56PyPWelRQHmQo6766q_p5Ff_fGTHJizifKbSuwvIfq6IT7Nd7u49G2mGQgy7MAoHLchnpDUZx_BvxtxvvTRVcPa_UeYpjQTTx5T14wHHTTQRxJeCL-T1zydMKIF2k8gTDeSlSA'
USER_TOKEN = 'vk1.a.gX9cGVskW7dPPYFmcv-7J5ALkHfM0m5xt-05vFfQisXYQ-QJfqF9atjG0mp35tqUQM549dWMRwjDzWtWu1MU0WpT3JCQQAFI2ndEuDxM1XfugJF8lGeCv4l6eTBN-jHI5oQb6IflGIVPB-DX-AYeYWgVE7SuCJjQUlCBq-ROHr5wU23OLsjUgLMXY6RPrsT3UChy4mB5lIQPgcjFcm0nNA'


vk_session = vk_api.VkApi(token=USER_TOKEN)
vk_group = vk_api.VkApi(token=COMMUNITY_TOKEN)
group_id = 216626916
longpoll = VkBotLongPoll(vk_session, group_id)


def start():
        favourites = []
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                peer_id = event.obj['message']['peer_id']
                user_info = get_user_info(vk_session, peer_id)
                app_user = User(user_id=peer_id,
                                first_name=user_info[0]['first_name'],
                                last_name=user_info[0]['last_name'])
                req_city_id = user_info[0]['city']['id']
                if user_info[0]['sex'] == 1:
                    req_sex = 2
                elif user_info[0]['sex'] == 2:
                    req_sex = 1
                while True:
                    if app_user.stage == 0:
                        send_message(vk_group, peer_id,
                                     "Привет!\nМеня зовут VKinder, и я - бот для поиска пары.\n"
                                     "Укажи интересующий тебя возрастной диапазон\nВ формате '18 99', где:\n"
                                     "18 - минимальный возраст,\n99 - максимальный возраст")
                        app_user.stage += 1
                    for event in longpoll.listen():
                        if event.type == VkBotEventType.MESSAGE_NEW:
                            words = event.obj['message']['text'].split()
                            if len(words) != 2:
                                send_message(vk_group, peer_id,
                                             'Возрастной диапазон задан не верно\n'
                                             'Перезапуск...')
                                app_user.stage = 0
                                break
                            try:
                                int(words[0])
                                int(words[1])
                            except Exception:
                                send_message(vk_group, peer_id,
                                             'Возрастной диапазон задан не верно\n'
                                             'Перезапуск...')
                                app_user.stage = 0
                                break
                            age_from = int(words[0])
                            age_to = int(words[1])
                            if age_to < age_from:
                                send_message(vk_group, peer_id,
                                             'Возрастной диапазон задан не верно\n'
                                             'Перезапуск...')
                                app_user.stage = 0
                                break
                            send_message(vk_group, peer_id,
                                         f"Ок. Буду искать не моложе {age_from}"
                                         f" и не старше {age_to} лет.\nНачинаем(Да/Нет)")
                            app_user.search_filter = UserSearchFilter(city_id=req_city_id, sex=req_sex,
                                                                              age_from=age_from, age_to=age_to)
                            user_mathcing = UserMatching(vk_session=vk_session, current_user=app_user)
                            app_user.stage += 1
                            while app_user.stage == 2:
                                for event in longpoll.listen():
                                    if event.type == VkBotEventType.MESSAGE_NEW:
                                        if event.obj['message']['text'].lower() == 'да':
                                            send_message(vk_group, peer_id, "Ищу...")
                                            user_mathcing.next()
                                            variant = user_mathcing.next()
                                            if variant is not None:
                                                photos = get_popular_photos(vk_session, variant['id'])
                                                send_message(vk_group, peer_id,
                                                             f"{variant['first_name']} {variant['last_name']}\n"
                                                             f"https://vk.com/id{variant['id']}\n",
                                                             reply_to=event.obj['message']['id'],
                                                             attachments=list(map(get_photo_attachment_link, photos)))
                                                send_message(vk_group, peer_id,
                                                             "\n\n1 - добавить в Избранное\n"
                                                             "0 - просмотреть Избранное\n"
                                                             "R - начать сначала\n\n"
                                                             "Продолжить поиск? (Да/Нет)\n")
                                            else:
                                                send_message(vk_group, peer_id,
                                                             "Похоже больше я не смогу ничего найти.\n"
                                                             "0 - просмотреть Избранное\n"
                                                             "R - начать сначала")
                                        elif event.obj['message']['text'] == '1':
                                            send_message(vk_group, peer_id,
                                                         "Добавляю в Избранное...\n\n"
                                                         "0 - просмотреть Избранное\n"
                                                         "R - начать сначала\n"
                                                         "Продолжить поиск? (Да/Нет)")
                                            favourites.append(variant['id'])
                                        elif event.obj['message']['text'] == '0':
                                            send_message(vk_group, peer_id, "Избранное:")
                                            for favourite in favourites:
                                                favourite_info = get_user_info(vk_session, favourite)
                                                favourite_name = favourite_info[0]['first_name']
                                                favourite_surname = favourite_info[0]['last_name']
                                                photos = get_popular_photos(vk_session, favourite)
                                                send_message(vk_group, peer_id,
                                                             message=f"\n\n{favourite_name} {favourite_surname}\n"
                                                                     f"https://vk.com/id{favourite}\n",
                                                             reply_to=event.obj['message']['id'],
                                                             attachments=list(map(get_photo_attachment_link, photos)))
                                            send_message(vk_group, peer_id,
                                                         "\n\nR - начать сначала"
                                                         "\nПоискать ещё? (Да/Нет)")
                                        elif event.obj['message']['text'].lower() == 'нет':
                                            send_message(vk_group, peer_id,
                                                         "Поиск остановлен.\nДа - поиск\n "
                                                         "0 - просмотреть Избранное\n"
                                                         "R - начать сначала")
                                        elif event.obj['message']['text'].lower() == 'r':
                                            send_message(vk_group, peer_id,
                                                         "Перезапуск...\n"
                                                         "Избранные сохраняются\n")
                                            app_user.stage = 0
                                            break
                            break

