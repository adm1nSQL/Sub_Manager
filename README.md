# SubManager

一个用 Telegram bot api 来管理跨境服务提供商的订阅平台。

## 快速开始

* 从 [@BotFather](https://t.me/BotFather) 那里创建一个机器人，获得该机器人的bot_token，应形如：

    bot_token = "xxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxx"

    这步不会请Google。
* 动动你的小手拉取本项目的源码
```shell
apt install -y git && git clone https://github.com/adm1nSQL/Sub_Manger.git && cd Sub_Manger
```

* 安装依赖 Python 3.6 以上



您可以用以下命令，在当前项目目录下运行以快速安装环境：

Windows:

```
pip install -r requirements.txt
```

Linux:

```
pip3 install -r requirements.txt
```

* 运行

首次运行需传入参数：
```shell
python3 main.py -s <超级管理员的TG_ID> -a <超级管理员的TG_ID,管理员1的TG_ID> -t <bot_token>
```
！！！运行时去掉<>

下次运行直接:
```shell
python main.py
```


