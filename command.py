# 添加数据
import struct
import shutil
import os
import telebot


def add_sub(message, **kwargs):
    c = kwargs.get('cursor', None)
    bot = kwargs.get('bot', None)
    conn = kwargs.get('conn', None)
    try:
        url_comment = message.text.split()[1:]
        url = url_comment[0]
        comment = url_comment[1]
        c.execute("SELECT * FROM My_sub WHERE URL=?", (url,))
        if c.fetchone():
            bot.reply_to(message, "😅订阅已存在！")
        else:
            c.execute("INSERT INTO My_sub VALUES(?,?)", (url, comment))
            conn.commit()
            bot.reply_to(message, "✅添加成功！")
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😵😵输入格式有误，请检查后重新输入")


# 删除数据
def delete_sub(message, **kwargs):
    c = kwargs.get('cursor', None)
    bot = kwargs.get('bot', None)
    conn = kwargs.get('conn', None)
    try:
        row_num = message.text.split()[1]
        c.execute("DELETE FROM My_sub WHERE rowid=?", (row_num,))
        conn.commit()
        c.execute("VACUUM")
        conn.commit()
        bot.reply_to(message, "✅删除成功！")
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😵😵输入格式有误，请检查后重新输入")


# 查找数据
items_per_page = 10
result = None
callbacks = {}


def search_sub(message, **kwargs):
    global items_per_page, total, result, current_page
    c = kwargs.get('cursor', None)
    bot = kwargs.get('bot', None)
    try:
        search_str = message.text.split()[1]
        c.execute("SELECT rowid,URL,comment FROM My_sub WHERE URL LIKE ? OR comment LIKE ?",
                  ('%' + search_str + '%', '%' + search_str + '%'))
        result = c.fetchall()
        if result:
            pages = [result[i:i + items_per_page] for i in range(0, len(result), items_per_page)]
            total = len(pages)
            current_page = 1
            current_items = pages[current_page - 1]
            keyboard = []
            for item in current_items:
                button = telebot.types.InlineKeyboardButton(item[2], callback_data=item[0])
                keyboard.append([button])
            if total > 1:
                page_info = f'第 {current_page}/{total} 页'
                prev_button = telebot.types.InlineKeyboardButton('上一页', callback_data='prev')
                next_button = telebot.types.InlineKeyboardButton('下一页', callback_data='next')
                page_button = telebot.types.InlineKeyboardButton(page_info, callback_data='page_info')
                page_buttons = [prev_button, page_button, next_button]
                keyboard.append(page_buttons)
            keyboard.append([telebot.types.InlineKeyboardButton('❎结束搜索', callback_data='close')])
            reply_markup = telebot.types.InlineKeyboardMarkup(keyboard)
            sent_message = bot.reply_to(message, f'卧槽，天降订阅🎁发现了{str(len(result))}个目标，快点击查看⏬', reply_markup=reply_markup)
            global sent_message_id
            sent_message_id = sent_message.message_id
            user_id = message.from_user.id
            callbacks[user_id] = {'total': total, 'current_page': current_page, 'result': result,
                                  'sent_message_id': sent_message_id}
        else:
            bot.reply_to(message, '😅没有查找到结果！')
    except Exception as t:
        print(t)
        bot.send_message(message.chat.id, "😵😵您输入的内容有误，请检查后重新输入")


# 更新数据
def update_sub(message, **kwargs):
    c = kwargs.get('cursor', None)
    bot = kwargs.get('bot', None)
    conn = kwargs.get('conn', None)
    try:
        row_num = message.text.split()[1]
        url_comment = message.text.split()[2:]
        url = url_comment[0]
        comment = url_comment[1]
        c.execute("UPDATE My_sub SET URL=?, comment=? WHERE rowid=?", (url, comment, row_num))
        conn.commit()
        bot.reply_to(message, "✅更新成功！")
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "😵😵输入格式有误，请检查后重新输入")


# 使用帮助
def help_sub(message, **kwargs):
    bot = kwargs.get('bot', None)
    doc = '''
🌈使用说明：
    1. 添加数据：/add url 备注
    2. 删除数据：/del 行数
    3. 查找数据：/search 内容
    4. 修改数据：/update 行数 订阅链接 备注
    5. 导入xlsx表格：发送xlsx或xls表格（注意文件格式！A列为订阅地址，B列为对应的备注）
    6. 备份数据库：私聊发送 /backup ，该功能仅限超级管理员
    7. 日志输出： 私聊发送 /log ，该功能仅限超级管理员
    
☎️*TG_Channel: @fffffx2 *
    '''
    bot.send_message(message.chat.id, doc, parse_mode='Markdown')


# 数据库备份
def backup(message, **kwargs):
    bot = kwargs.get('bot', None)
    try:
        backup_dir = './backup'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        backup_file = os.path.join(backup_dir, 'My_sub_backup.db')
        shutil.copyfile('My_sub.db', backup_file)
        with open(backup_file, 'rb') as file:
            bot.send_document(message.chat.id, file)
        for file in os.listdir(backup_dir):
            if file != 'My_sub_backup.db':
                os.remove(os.path.join(backup_dir, file))
        bot.reply_to(message, "✅数据库备份完成")
    except Exception as t:
        bot.reply_to(message, f"⚠️出现问题了，报错内容为: {t}")


# 日志输出
def log(message, **kwargs):
    bot = kwargs.get('bot', None)
    try:
        with open('./bot.log', 'rb') as f:
            bot.send_document(message.chat.id, f)
            f.close()
    except Exception as t:
        bot.reply_to(message, f"⚠️出错了: {t}")


class file_analyze:
    # 来源于网络
    # 支持文件类型
    # 用16进制字符串的目的是可以知道文件头是多少字节
    # 各种文件头的长度不一样，少半2字符，长则8字符
    @staticmethod
    def typeList():
        return {
            "504B0304": 'EXT_ZIP/XLSX/DOCX',
            "D0CF11E0": 'XLS/DOC'
        }

        # 字节码转16进制字符串

    @staticmethod
    def bytes2hex(_bytes):
        num = len(_bytes)
        hexstr = u""
        for i in range(num):
            t = u"%x" % _bytes[i]
            if len(t) % 2:
                hexstr += u"0"
            hexstr += t
        return hexstr.upper()

    # 获取文件类型

    @staticmethod
    def filetype(filename):
        binfile = open(filename, 'rb')  # 必需二制字读取
        tl = file_analyze.typeList()
        ftype = 'unknown'
        for hcode in tl.keys():
            numOfBytes = int(len(hcode) / 2)  # 需要读多少字节
            binfile.seek(0)  # 每次读取都要回到文件头，不然会一直往后读取
            hbytes = struct.unpack("B" * numOfBytes, binfile.read(numOfBytes))  # 一个 "B"表示一个字节
            f_hcode = file_analyze.bytes2hex(hbytes)
            if f_hcode == hcode:
                ftype = tl[hcode]
                break
        binfile.close()
        return ftype


if __name__ == '__main__':
    pass
