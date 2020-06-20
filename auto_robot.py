import time
import itchat
import requests
from itchat.content import *
import os
import style_trans
import re

# 文件临时存储页
rec_tmp_dir = os.path.join(os.getcwd(), 'photo/')
# 存储数据的字典
rec_msg_dict = {}
frontFriend = '0'
option=0  #风格迁移的步骤
epochs=10   #训练轮数
choose=8    #选择的图片
tick=0

# 好友信息监听，自定义图片下载模块
@itchat.msg_register([TEXT, PICTURE, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True)
def handle_friend_msg(msg):
    global option,epoches,choose
    msg_id = msg['MsgId']
    msg_from_user = msg['User']['NickName']
    msg_content = ''
    # 收到信息的时间
    msg_time_rec = time.strftime("%Y-%m-%d %H:%M%S", time.localtime())
    msg_create_time = msg['CreateTime']
    msg_type = msg['Type']

    if msg['Type'] == 'Text':
        msg_content = msg['Content']
    elif msg['Type'] == 'Picture' \
            or msg['Type'] == 'Recording' \
            or msg['Type'] == 'Video' \
            or msg['Type'] == 'Attachment':
        msg_content = r"" + msg['FileName']
        msg['Text'](rec_tmp_dir + msg['FileName'])
    rec_msg_dict.update({
        msg_id: {
            'msg_from_user': msg_from_user,
            'msg_time_rec': msg_time_rec,
            'msg_create_time': msg_create_time,
            'msg_type': msg_type,
            'msg_content': msg_content
        }
    })
    print(msg)
    if option == 1:
        number=style_trans.begin_style_trans(epochs,choose)
        itchat.send_image('./result/'+number+'.jpg', msg["FromUserName"])
        print("发送图片完毕")
        option = 0


#获取图灵机器人回复模块
def get_tuling_reponse(_info):
    print(_info)
    api_url = 'http://www.tuling123.com/openapi/api'
    data = {
        'key': 'e6e3196934e94cf98bfd09b16cd3c122',
        'info': _info,
        'userid': 'haha'
    }
    # 发送数据到指定的网址，获取网址返回的数据
    res = requests.post(api_url, data).json()
    print(res,type(res))
    # 给用户返回的内容
    print(res['text'])
    return (res['text'])




# 时刻监控好友发送的文本信息，并且给与一个回复
@itchat.msg_register(itchat.content.TEXT, isFriendChat=True)
def text_repky(msg):
    global frontFriend
    global option
    global epochs
    global choose
    global tick

    print(msg)

    print(option)
    if option == 0:
        if "风格迁移" in msg['Text']:
            option = 1
            itchat.send_image(r'C:\Users\Administrator\Desktop\style_trans-master\total.jpg', msg["FromUserName"])
            return "请发送你要进行风格迁移的风格图片\n(拓展：发送“风格图片:数字” 自定义选择风格)"    #  \n发送“风格影响:数字”选择图片风格的影响大小（建议5~10）
    if "风格图片" in msg["Text"]:
        choose = int(re.sub("\D", "", msg["Text"]))
        return "风格图片选择成功"

    if "风格影响" in msg["Text"]:
        epochs=int(re.sub("\D", "", msg["Text"]))
        return "风格影响大小调整成功"



    if msg['FromUserName'] == frontFriend:
        if ((time.time()-tick)<5):
            print("同一个用户连续发送,不默认回复了")
            return

    frontFriend = msg['FromUserName']
    tick = time.time()
    content = msg['Content']
    time.sleep(2.5)
    #returnContent='.....'
    returnContent = get_tuling_reponse(content)
    return returnContent


#登录模块
itchat.auto_login(hotReload=False)
itchat.run()





















# # 爬虫
# def findimginhtml(url):
#     require = urllib.request.Request(url)
#     reponse = urllib.request.urlopen(require)
#     html = reponse.read()
#     regx = 'https[\S]*qhimgs1.com[\S]*jpg'
#
#     pattern = re.compile(regx)
#     get_image = re.findall(pattern, repr(html))
#     wrap = '{' + get_image[0] + '"}'
#     wrap = wrap[wrap.find('}') + 2:].replace("false", "False")
#     wrapdict = eval(wrap)
#     print("抓到图片张数:" + str(len(wrapdict)))
#     # 随机选取一张
#     randomimg = wrapdict[random.randint(1, len(wrapdict))]['thumb']
#     randomimg = randomimg.replace("\\", "")
#     print("随机抓取一张图片:" + randomimg)
#     return randomimg
#
#
# # 下载图片
# def downloadpic(url):
#     img = requests.get(url)
#     filename = time.strftime("%Y-%m-%d", time.localtime()) + "-" + str(uuid.uuid4())
#     with open("../img/{}.jpg".format(filename), 'wb') as f:
#         f.write(img.content)
#         print("下载图片...")
#     print("下载完毕")
#     return "../img/" + filename + ".jpg"
#
#
# # 图灵API调用
# html = tulingRobotReply(message)
# # 解析返回结果的的url
# imgurl = re.findall(r'\"url\"\:\".*?\"', html)
# webimgurl = ":".join(imgurl[0].split(':')[1:])
# print("图片地址:" + webimgurl)
# # 发送，测试可用filehelper作为接收方
# itchat.send_image(downloadpic(findimginhtml(webimgurl.replace("\"", ""))), 'filehelper


