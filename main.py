import telebot
from time import sleep
from loguru import logger
from bot import loader

# 1.22增加了日志功能，记录用户使用的指令和获取的订阅日志
logger.add('bot.log')

# 定义bot管理员的telegram userid ['1881396047']
admin_id = []

# 定义bot
bot_token = ''


    print('=====程序已启动=====')
    while True:
        try:
            loader(bot, admin_id=admin_id)
            bot.polling(none_stop=True)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            sleep(30)
