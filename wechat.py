import os
import bm25
import bot
import itchat, time
from datetime import datetime
import random
from itchat.content import *
from pprint import pprint
from collections import defaultdict

Wechat_files = "/Users/gus/library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9"

CHATROOM = "猪猪🐼和小猪友😀"
MYSELF = "Gus"
ZSL = "🦊"
STOP_WORD = "猪猪要讲话啦"
START_WORD = "猪猪讲完"

DEBUG = False
SAY_FLAG = False
BM25_love = None
Boring_MAX = 3
IMAGE_P = 0.9
GIF_P = 0.3

Start_hour = 0
End_hour = 7

SEP = "------------------------------------------------------------------------"

with open("./asset/non_reply.txt", 'r') as f:
    NON_REPLY = [l.strip() for l in f.readlines()]

with open("./asset/love_story.txt", 'r') as f:
    LOVE_STORY = [l.strip() for l in f.readlines()]
    LOVE_COUNT = defaultdict(int)

with open("./asset/emoji.txt", 'r') as f:
    EMOJI = [l.strip() for l in f.readlines()]

LOVE_trigger = [
    "想你", "情话", "老公"
]

def has_keyword(msg_str, keys):
    for k in keys:
        if k in msg_str:
            return True
    return False

def get_gif():
    all_gif = [f for f in os.listdir("./gifs") if f.endswith("gif")]
    return os.path.join("./gifs", get_random(all_gif))

def get_image():
    all_img = [f for f in os.listdir("./imgs") if f.endswith("jpg")]
    return os.path.join("./imgs", get_random(all_img))

def get_random(msg_list):
    choice = random.randint(0, len(msg_list)-1)
    return msg_list[choice]

def get_hour():
    return int(datetime.now().strftime("%H"))

def send(msg, msg_str):
    msg.user.send(msg_str)

def send_img(msg, img_file):
    msg.user.send(f"@img@{img_file}")


def get_love_line(msg):
    if msg.type == TEXT:
        query = str(msg.content)
        index = bm25.search(BM25_love, query)
        for i in index:
            if LOVE_COUNT[i] < Boring_MAX:
                chat = LOVE_STORY[i]
                LOVE_COUNT[i] += 1
                break
    else:
        chat = get_random(LOVE_STORY)
    chat = template(chat)
    emo = get_random(EMOJI)
    msg.user.send(chat + emo)


def get_BM25(lines : list):
    import bm25
    corpus = bm25.generate_corpus(lines)
    model  = bm25.get_BM25(corpus)
    return model

def is_working():
    # return (Start_hour <= get_hour() <= End_hour) and not DEBUG
    return not DEBUG

def is_me(msg):
    return str(msg.ActualNickName) == MYSELF

def is_gif(msg):
    return str(msg.FileName).endswith("gif")


def template(msg : str):
    msg = msg.replace("{time}", datetime.now().strftime("%H:%M"))
    return msg

def Chat(msg):
    global BM25_love
    if has_keyword(str(msg.content), LOVE_trigger):
        if BM25_love is None:
            BM25_love = get_BM25(LOVE_STORY)
        get_love_line(msg)
        return
    send(msg, bot.qingyunke(str(msg.content)))
    if random.random() > IMAGE_P:
        send_img(msg, get_image())
    return

@itchat.msg_register(
    [TEXT, MAP, CARD, NOTE, SHARING, PICTURE, RECORDING, ATTACHMENT, VIDEO])
def debug(msg):
    global DEBUG
    if str(msg.ToUserName) == "filehelper":
        print(SEP)
        if msg.type == TEXT and "debug" == str(msg.content).strip():
            if not DEBUG:
                msg.user.send("DEBUG")
            else:
                msg.user.send("DEBUG off")
            DEBUG = False if DEBUG else True
            return
        if DEBUG and msg.type == TEXT:
            try:
                results = str(eval(str(msg.content).strip()))
            except:
                results = "Wrong"
            msg.user.send("GET " + str(msg.content).strip())
            msg.user.send("RET " + results)
            return
        if msg.type not in [PICTURE, RECORDING, ATTACHMENT, VIDEO]:
            Chat(msg)
            print("ME send", msg.type, msg.content)
        else:
            if is_gif(msg):
                save_to = "./gifs/" + str(msg.FileName)
                msg.download(save_to)
            print("ME send", msg.type, msg.FileName)

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def media_reply(msg):
    if not is_working():
        return
    if str(msg.User.NickName) == CHATROOM and not is_me(msg):
        if is_gif(msg):
            if random.random() > GIF_P:
                send_img(msg, get_gif())
            return
        msg.user.send(get_random(NON_REPLY))
        # pprint(msg)


@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    global SAY_FLAG, DEBUG
    if not is_working():
        return
    if str(msg.User.NickName) == CHATROOM and not is_me(msg):
        if msg.content.strip() == STOP_WORD:
            send(msg, "好的, 我听着呢😊")
            DEBUG = True
            return
        if msg.content.strip() == START_WORD:
            send(msg, "我开始逼逼了🐎")
            DEBUG = False
            return
        return Chat(msg)


itchat.auto_login(hotReload=True)
itchat.run(True)
