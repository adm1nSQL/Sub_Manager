import sqlite3
import pandas as pd
from loguru import logger
from command import *

# 定义数据库
conn = sqlite3.connect('My_sub.db', check_same_thread=False)
c = conn.cursor()

# 创建表
c.execute('''CREATE TABLE IF NOT EXISTS My_sub(URL text, comment text)''')


def loader(bot: telebot.TeleBot, **kwargs):
    command_loader(bot, **kwargs)
    callback_loader(bot, **kwargs)


def command_loader(bot: telebot.TeleBot, **kwargs):
    super_admin = kwargs.get('super_admin', '')
    admin_id = kwargs.get('admin_id', [])

    # 接收用户输入的指令
    @bot.message_handler(commands=['add', 'del', 'search', 'update', 'help', 'backup', 'log'])
    def handle_command(message):
        command = message.text.split()[0]
        if str(message.from_user.id) in admin_id:
            logger.debug(f"用户{message.from_user.id}使用了{command}功能")
            if command == '/add':
                add_sub(message, cursor=c, conn=conn, bot=bot)
            elif command == '/del':
                delete_sub(message, cursor=c, conn=conn, bot=bot)
            elif command == '/search':
                search_sub(message, cursor=c, conn=conn, bot=bot)
            elif command == '/update':
                update_sub(message, cursor=c, conn=conn, bot=bot)
            elif command == '/help':
                help_sub(message, bot=bot)
        else:
            bot.reply_to(message, "❌你没有操作权限，别瞎搞！")
        if str(message.from_user.id) == super_admin:
            try:
                if command == '/backup' and message.chat.type == 'private':
                    backup(message, **kwargs, bot=bot)
                    logger.debug(f"用户{message.from_user.id}备份了数据库")
                elif command == '/log' and message.chat.type == 'private':
                    log(message, **kwargs, bot=bot)
            except Exception as e:
                bot.reply_to(message, f"⚠️发生错误：{e}")
        elif str(message.from_user.id) in admin_id:
            pass
        else:
            bot.reply_to(message, "🈲该操作仅限超级管理员！")

    # 接收xlsx表格
    @logger.catch()
    @bot.message_handler(content_types=['document'], chat_types=['private'])
    def handle_document(message):
        if str(message.from_user.id) in admin_id:
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            try:
                file = bot.download_file(file_info.file_path)
                with open('sub.xlsx', 'wb') as f:
                    f.write(file)
                if file_analyze.filetype('sub.xlsx') in ['EXT_ZIP/XLSX/DOCX', 'XLS/DOC']:
                    df = pd.read_excel('sub.xlsx')
                    for i in range(len(df)):
                        c.execute("SELECT * FROM My_sub WHERE URL=?", (df.iloc[i, 0],))
                        if not c.fetchone():
                            c.execute("INSERT INTO My_sub VALUES(?,?)", (df.iloc[i, 0], df.iloc[i, 1]))
                            conn.commit()
                    bot.reply_to(message, "✅导入成功！")
                else:
                    bot.send_message(message.chat.id, "😵😵导入的文件格式错误，请检查文件后缀是否为xlsx后重新导入")
            except Exception as e:
                print(e)

        else:
            bot.reply_to(message, "😡😡😡你不是管理员，禁止操作！")


def callback_loader(bot: telebot.TeleBot, **kwargs):
    admin_id = kwargs.get('admin_id', [])

    # 按钮点击事件
    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        if str(call.from_user.id) in admin_id:
            if call.data == 'close':
                bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                try:
                    row_num = call.data
                    c.execute("SELECT rowid,URL,comment FROM My_sub WHERE rowid=?", (row_num,))
                    result = c.fetchone()
                    bot.send_message(call.message.chat.id,
                                     '行号：{}\n订阅地址：{}\n说明： {}'.format(result[0], result[1], result[2]))
                    logger.debug(f"用户{call.from_user.id}从BOT获取了{result}")
                except Exception as e:
                    print(e)
                    bot.send_message(call.message.chat.id, f"{e}")
        else:  # 弹窗提示来自 @cpploveme ，合并失误手动添加
            try:
                bot.answer_callback_query(call.id, f"天地三清，道法无敌，邪魔退让！退！退！退！👮‍", show_alert=True)
            except:
                pass
