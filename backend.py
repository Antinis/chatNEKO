#!/usr/bin/env python3

from flask import Flask, request
import os
import openai;
import requests;
import json;
import re;
import argparse;
from search_researchers.Retrieve import bot_api;
import pdb;

app = Flask(__name__)

'''监听端口，获取QQ信息'''
@app.route('/', methods=["POST"])
def post_data():
    global msg;
    if request.get_json().get('message_type')=='group':
        gid = request.get_json().get('group_id')
        message = request.get_json().get('raw_message')
        handle(gid, message);

    return 'OK'


def chat(user_message, gid):
    global msg;
    user_msg_dict={
        "role": "user",
        "content": user_message
    };
    msg.append(user_msg_dict);

    # 结构化数据并进行提交
    completion = openai.ChatCompletion.create(
        # max_tokens = 2,           # 默认inf 最大令牌数
        presence_penalty = 0,       # 惩罚机制，-2.0 到 2.0之间，默认0，数值越小提交的重复令牌[>
        frequency_penalty = 0,      # 意义和值基本同上，默认0，主要为频率
        temperature = 1.0,          # 温度 0-2之间，默认1  调整回复的精确度使用
        n = 1,                      # 默认条数1
        user = "user",              # 用户ID，用于机器人区分不同用户避免多用户时出现混淆
        model = "gpt-3.5-turbo",    # 这里注意openai官方有很多个模型
        messages = msg
    )
    assi_msg = completion.choices[0].message.content    # chatGPT返回的数据
    assi_msg_dict={
        "role": "assistant",
        "content": assi_msg
    };
    msg.append(assi_msg_dict);

    if len(msg)>10:
        msg=msg[2:]

    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(str(gid), assi_msg));

    return;

def setu(keyword, gid):
    id=search_pic(keyword);
    if id==-1:
        requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message=已经没有好看的图啦！".format(str(gid)));
        return;
    else:
        path=download_pic(id);
        send_pic(gid, path);

def search_gs(sch_args, gid):
    if args.use_proxy:
        sch_args+=f" --http_proxy {args.proxy_addr}";
        sch_args+=f" --https_proxy {args.proxy_addr}";
    else:
        sch_args+=f" --no_proxy";
    if " --not_save" not in sch_args:
        sch_args+=" --not_save";
    sch_msg=f"传入指令为\'{sch_args}\'";
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(str(gid), sch_msg));
    sch_msg="正在搜索喵～";
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(str(gid), sch_msg));
    try:
        sch_msg=bot_api(sch_args);
    except:
        sch_msg="检索失败了喵！";
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(str(gid), sch_msg));
    return;

def search_pic(keyword):
    if args.use_proxy:
        proxies={
            'http':args.proxy_addr,
            'https':args.proxy_addr
        };
    search_url="https://www.pixiv.net/ajax/search/artworks/"+keyword+" 1000users入り";
    if args.use_proxy:
        r=requests.get(url=search_url, proxies=proxies);
    else:
        r=requests.get(url=search_url);
    search_json=r.text;
    img_list=json.loads(search_json)["body"]["illustManga"]["data"];

    for i in range(len(img_list)):
        id=img_list[i]["id"];
        if not _exists(id):
            try:
                with open("used.txt",mode="a") as f:
                    f.write(id+"\n");
            except:
                os.makedirs("used.txt");
                with open("used.txt",mode="a") as f:
                    f.write(id+"\n");
            return id;

    # 没有搜索到热门插画，降低搜索标准继续搜索
    search_url="https://www.pixiv.net/ajax/search/artworks/"+keyword+" 500users入り";
    if args.use_proxy:
        r=requests.get(url=search_url, proxies=proxies);
    else:
        r=requests.get(url=search_url);
    search_json=r.text;
    img_list=json.loads(search_json)["body"]["illustManga"]["data"];

    for i in range(len(img_list)):
        id=img_list[i]["id"];
        if not _exists(id):
            with open("used.txt",mode="a") as f:
                f.write(id+"\n");
            return id;

    search_url="https://www.pixiv.net/ajax/search/artworks/"+keyword+" 100users入り";
    if args.use_proxy:
        r=requests.get(url=search_url, proxies=proxies);
    else:
        r=requests.get(url=search_url);
    search_json=r.text;
    img_list=json.loads(search_json)["body"]["illustManga"]["data"];

    for i in range(len(img_list)):
        id=img_list[i]["id"];
        if not _exists(id):
            with open("used.txt",mode="a") as f:
                f.write(id+"\n");
            return id;

    search_url="https://www.pixiv.net/ajax/search/artworks/"+keyword;
    if args.use_proxy:
        r=requests.get(url=search_url, proxies=proxies);
    else:
        r=requests.get(url=search_url);
    search_json=r.text;
    img_list=json.loads(search_json)["body"]["illustManga"]["data"];

    for i in range(len(img_list)):
        id=img_list[i]["id"];
        if not _exists(id):
            with open("used.txt",mode="a") as f:
                f.write(id+"\n");
            return id;
    
    return -1;

def _exists(id):
    usedIDtxt="";
    try:
        with open("used.txt",mode="r") as f:
            usedIDtxt=f.read();
    except:
        pass;
    usedIDList=usedIDtxt.split();

    flag=False;
    for used_id in usedIDList:
        if used_id==id:
            flag=True;
            break;
    
    if flag==True:
        return True;
    else:
        return False;

def download_pic(id):
    mainpage_url='http://www.pixiv.net';
    UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.29';
    Headers={
        'Referer': mainpage_url,
        'User-Agent': UA,
        'Referer': 'https://www.pixiv.net/'
    };
    if args.use_proxy:
        proxies={
            'http':args.proxy_addr,
            'https':args.proxy_addr
        };

    showurl="https://www.pixiv.net/artworks/"+id;
    if args.use_proxy:
        r=requests.get(showurl, headers=Headers, proxies=proxies);
    else:
        r=requests.get(showurl, headers=Headers);
    html=r.text;
    
    comp=re.compile(r'"original":"(?P<picurl>.*?)"},"tags":.*?',re.S);
    res=comp.finditer(html);
    fullpicurl="";
    for i in res:
        fullpicurl=i.group("picurl");
    if args.use_proxy:
        r=requests.get(url=fullpicurl, headers=Headers, proxies=proxies);
    else:
        r=requests.get(url=fullpicurl, headers=Headers);
    if(r.status_code!=200):
        return -1;
    
    mode=fullpicurl.split(".")[-1];
    path="";
    if mode=="jpg":
        path="img/"+str(id)+".jpg";
    elif mode=="png":
        path="img/"+str(id)+".png";
    else:
        print("Invalid image type!");
        exit();
    
    with open(path, mode="wb") as f:
        f.write(r.content);

    return path;

def send_pic(gid, path):
    dir=os.getcwd();
    path="file:///{}/{}".format(dir, path);
    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message=[CQ:image,file={},id=40000]".format(str(gid), path));
    return;

def handle(gid, message):
    if gid == args.group_id:   # 目前只向特定群提供服务
        if "[CQ:at,qq={}]".format(args.qq_id) in message:  # 呼出bot
            user_msg=message.replace("[CQ:at,qq={}] ".format(args.qq_id), ""); # 切掉信头

            if user_msg.split(" ")[0]=="chat":  # 呼出chatGPT服务
                if user_msg=="chat clear":       # 清除chatGPT上下文指令
                    global msg;
                    msg=[];
                    requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(args.group_id, "已清除上下文"));
                    return;
                chat(user_msg.replace("chat ", ""), gid);
                return;
            
            if user_msg.split(" ")[0]=="setu":  # 呼出pixiv搜图服务
                setu(user_msg.replace("setu ", ""), gid);
                return;

            if user_msg.split(" ")[0]=="search": # 呼出Google Scholar快速搜索服务
                search_gs((user_msg).replace("search ", ""), gid);
                return;

            requests.get("http://127.0.0.1:5700/send_group_msg?group_id={}&message={}".format(args.group_id, 
            "这里是chatNEKO喵，使用方法：\n\n" + 
            "1. chatGPT聊天\n   @chatNEKO chat *聊天内容*\n\n" + 
            "2. 清除chatGPT上下文并开始新会话\n   @chatNEKO chat clear\n\n" + 
            "3. pixiv插画搜索\n   @chatNEKO setu *关键词*\n\n" + 
            "4. Google Scholar 快速检索\n   @chatNEKO search *搜索指令*，用法请参考search_researchers/README.md\n\n" + 
            "请注意，“@chatNEKO”标识符只有在手动键盘输入并选择用户时才能生效。直接从剪贴板粘贴“@chatNEKO”无效。\n\n" + 
            "Github项目地址为 https://github.com/Antinis/chatNEKO 希望更多功能或建议请联系作者Antinis zhangyunxuan@zju.edu.cn\n\n快来跟我玩喵~"));

global msg;
msg=[];
parser=argparse.ArgumentParser(description='test')
parser.add_argument('--qq_id', default=False, type=int, help='QQ id of the bot')
parser.add_argument('--group_id', default=False, type=int, help='Which QQ group do you want to arrange this bot?')
parser.add_argument('--openai_key', default=False, type=str, help='The key of OpenAI ChatGPT API')
parser.add_argument('--use_proxy', default=False, type=bool, help='Whether to use proxy server? If you are using Chinese network service and you want to use pixiv illustration searching function, you may set this argument as True.')
parser.add_argument('--proxy_addr', default=False, type=str, help='The address and port of proxy server.')
args=parser.parse_args()

if args.openai_key:
    openai.api_key=args.openai_key;

app.run(debug=False, host='127.0.0.1', port=5701)