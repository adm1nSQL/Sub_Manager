import getopt
import sys
import json
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

if __name__ == '__main__':
    # 命令行参数处理
    if len(sys.argv) == 1:
        try:
            with open('./config.json', 'r', encoding='utf-8') as fp:
                config = json.load(fp)
                admin_id = config.get('admin', [])
                bot_token = config.get('token', '')
        except FileNotFoundError:
            print('Usage:\n -a, --admin \t管理员名单id,多个id之间以英文逗号(,)间隔\n -t, --token \tTelegram机器人的bot_token')
            exit()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:t:", ["admin=", "token="])
    except getopt.GetoptError:
        print('Usage:\n -a, --admin \t管理员名单id,多个id之间以英文逗号(,)间隔\n -t, --token \tTelegram机器人的bot_token')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage(使用帮助):\n -a, --admin \t管理员名单id,多个id之间以英文逗号(,)间隔\n -t, --token \tTelegram机器人的bot_token')
            sys.exit()
        elif opt in ("-a", "--admin"):
            admin_id = arg.split(',')
        elif opt in ("-t", "--token"):
            bot_token = arg
    logger.info(f"管理员名单加载: {str(admin_id)}")
    with open('./config.json', 'w', encoding='utf-8') as fp:
        json.dump({'admin': admin_id, 'token': bot_token}, fp)
    if bot_token and admin_id:
        bot = telebot.TeleBot(bot_token)
    else:
        bot = None
        logger.warning("无管理员或bot_token,请检查输入的参数")
        exit()
    print('=====程序已启动=====')
    try:
        while True:
            loader(bot, admin_id=admin_id)
            bot.polling(none_stop=True)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print(e)
        sleep(30)
