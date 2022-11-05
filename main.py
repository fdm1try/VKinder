from VKinder.modules.db import model, storage
from VKinder.app import VKinder
import logging
import sys

MAX_ERROR_COUNT_PER_MINUTE = 10
LOGGING_FORMAT = '[%(levelname)s] %(asctime)s [user: %(name)s]: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT)


if __name__ == "__main__":
    if not storage.init():
        user_input = input(
            "База данных повреждена или не была создана. Создать базу данных (все данные будут утеряны)? (да/нет): "
        )
        if user_input.lower().startswith('д'):
            model.create_tables()
        else:
            print("Приложение остановлено.")
            sys.exit(1)
    error_log = []
    while 1:
        try:
            chat_bot = VKinder()
            print("Приложение запущено!")
            chat_bot.run()
        except vk_api.ApiError as error:
            if error.code == 5:
                logging.error(
                    "Не удалось запустить приложение, не указаны или указаны не верно переменные окружения "
                    f"VK_APP_ID, VK_GROUP_ID или VK_GROUP_TOKEN!\n\tVK API ERROR {error}"
                )
                sys.exit(error.code)
            elif error.code in [15, 100]:
                logging.error(
                    f"Вероятно не верно задано значение переменной окружения VK_GROUP_ID\n\tVK API ERROR {error}"
                )
                sys.exit(error.code)
            logging.error(f"VK API ERROR {error}")
        except Exception as error:
            logging.error(error)
        finally:
            now = datetime.now().timestamp()
            errors = [error for error in error_log if now - 60 < error]
            error_log.append(now)
            if len(error_log) >= MAX_ERROR_COUNT_PER_MINUTE:
                logging.error("Превышено максимальное количество ошибок в минуту, приложение остановлено!")
                sys.exit(1)
